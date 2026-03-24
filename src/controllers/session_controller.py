"""Session controller for handling HTTP requests for session parsing."""
from typing import Optional, cast
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
import logging
from src.service.postgres_service import PostgreService
from src.service.session_parser_service import SessionParserService
from src.service.session_file_service import SessionFileService
from src.service.session_type_service import SessionTypeService
from src.utils.file_utils import FileUtils
from src.validators.session_request_validator import SessionRequestValidator
from src.ai.ai_summarizer import AISummarizer


logger = logging.getLogger(__name__)


def create_app(db_config: Optional[dict] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        db_config: Optional database configuration dictionary with keys:
                  host, port, database, user, password
                  
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    
    # Initialize database connection
    if db_config is None:
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5433)),
            'database': os.getenv('DB_NAME', 'senate_db'),
            'user': os.getenv('DB_USER', 'senate_user'),
            'password': os.getenv('DB_PASSWORD', 'senate_pass')
        }
    
    postgres_service = PostgreService(**db_config)
    
    # Try to initialize AI Summarizer if environment variables are set
    summarizer = None
    try:
        if os.getenv('AZURE_OPENAI_API_KEY'):
            summarizer = AISummarizer()
            logger.info("AI Summarizer initialized successfully - intervention summaries will be generated")
    except Exception as e:
        logger.warning(
            "Could not initialize AI Summarizer - intervention summaries will not be generated: %s",
            e
        )
    
    session_parser_service = SessionParserService(postgres_service, summarizer=summarizer)
    session_file_service = SessionFileService(postgres_service)
    session_type_service = SessionTypeService(postgres_service)
    session_request_validator = SessionRequestValidator(session_type_service)
    
    @app.before_request
    def log_request():
        """Log all incoming requests."""
        logger.info("Incoming request: %s %s", request.method, request.path)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'session-parser'}), 200
    
    @app.route('/api/sessions/parse', methods=['POST'])
    def parse_session():
        """
        Parse a session PDF and store it in the database.
        
        Expected form data:
        - file: PDF file (required)
        - date: Session date in YYYY-MM-DD format (optional, can be inferred from filename)
        - session_type: Session type short name (optional, can be inferred from filename)
        - debug: Boolean flag for debug mode (optional, defaults to false)
        - force: Boolean flag to force re-parsing (optional, defaults to false)
        
        Returns:
            JSON response with parsing results or error message
        """
        # Validate request
        validation_result = session_request_validator.validate_parse_request(request)
        
        if not validation_result.success:
            return jsonify({'error': validation_result.error.message}), validation_result.error.status
        
        # Extract validated data
        file = validation_result.data['file']
        date_obj = validation_result.data['date']
        session_type_id = validation_result.data['session_type_id']
        debug = validation_result.data['debug']
        force = validation_result.data['force']
        topic = validation_result.data.get('topic')
        
        # Save file to temporary location
        temp_path = None
        try:
            # Create a temporary file
            temp_dir = tempfile.gettempdir()
            filename = secure_filename(file.filename)
            temp_path = os.path.join(temp_dir, f"session_{datetime.now().timestamp()}_{filename}")
            
            # Save the uploaded file
            file.save(temp_path)
            
            # Calculate file hash
            file_hash = FileUtils.calculate_file_hash(temp_path)
            file_size = os.path.getsize(temp_path)
            
            # Check if file was already parsed
            existing_file = session_file_service.get_by_hash(file_hash)
            
            if existing_file and not force:
                # File already parsed, return existing session info
                os.remove(temp_path)
                return jsonify({
                    'success': True,
                    'message': 'File already parsed (use force=true to re-parse)',
                    'already_parsed': True,
                    'data': {
                        'session_id': existing_file.SenateSession_id,
                        'file_hash': existing_file.File_hash,
                        'original_file_name': existing_file.File_name,
                        'upload_date': existing_file.Upload_date.isoformat()
                    }
                }), 200
            
            # If force=true and file exists, delete the old record
            if existing_file and force:
                session_file_service.delete_by_hash(file_hash)
            
            # Parse and store the session
            result = session_parser_service.parse_and_store_session(
                pdf_path=temp_path,
                session_date=date_obj,
                session_type_id=session_type_id,
                debug=debug,
                topic_filter=topic
            )
            
            # Debug: Log not found speakers (deduplicated)
            if 'not_found_speakers' in result:
                unique_speakers = sorted(set(result['not_found_speakers']))
                logger.info("=== Not Found Speakers (%s) ===", len(unique_speakers))
                for speaker in unique_speakers:
                    logger.info("  - %s", speaker)
                logger.info("===================")
            
            # Store file hash and metadata
            session_file_service.create(
                senate_session_id=result['session_id'],
                file_hash=file_hash,
                file_name=filename,
                file_size=file_size,
                upload_date=datetime.now()
            )
            
            # Clean up temporary file
            os.remove(temp_path)
            
            # Return success response
            return jsonify({
                'success': True,
                'message': 'Session parsed and stored successfully',
                'already_parsed': False,
                'data': {
                    'session_id': result['session_id'],
                    'session_date': result['session_date'].isoformat(),
                    'file_hash': file_hash,
                    'topics_stored': result['topics_stored'],
                    'interventions_stored': result['interventions_stored'],
                    'attendance_stored': result['attendance_stored'],
                    'topics_parsed': result['topics_parsed'],
                    'attendance_parsed': result['attendance_parsed'],
                    'index_items': result['index_items']
                }
            }), 201
            
        except Exception as e:
            # Clean up temporary file if it exists
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
            except (OSError):
                pass  # Ignore if cleanup fails
            
            # Return error response
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to parse session'
            }), 500
    
    @app.route('/api/sessions', methods=['GET'])
    def get_sessions():
        """
        Get all sessions from the database.
        
        Returns:
            JSON response with list of sessions
        """
        try:
            # This is a placeholder - you can implement this using SenateSessionService.get_all()
            return jsonify({
                'success': True,
                'message': 'Endpoint not yet implemented',
                'data': []
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app


if __name__ == '__main__':
    """Run the Flask application in development mode."""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
