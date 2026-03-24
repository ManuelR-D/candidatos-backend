"""Validator for session parsing requests."""
from typing import Optional, Any, cast
from datetime import datetime, date
from flask import Request
from werkzeug.datastructures import FileStorage
from src.service.session_type_service import SessionTypeService
from src.utils.file_utils import FileUtils


class ValidationError:
    """Validation error with message and status code."""
    
    def __init__(self, message: str, status: int):
        self.message = message
        self.status = status


class ValidationResult:
    """Result of validation - either success with data or failure with error."""
    
    def __init__(self, success: bool, data: Optional[dict[str, Any]] = None, error: Optional[ValidationError] = None):
        self.success = success
        self._data = data if data is not None else {}
        self._error = error
    
    @property
    def data(self) -> dict[str, Any]:
        """Get validated data. Should only be accessed when success=True."""
        if not self.success:
            raise RuntimeError("Cannot access data on failed validation")
        return self._data
    
    @property
    def error(self) -> ValidationError:
        """Get validation error. Should only be accessed when success=False."""
        if self.success or self._error is None:
            raise RuntimeError("Cannot access error on successful validation")
        return self._error


class SessionRequestValidator:
    """Validator for session parsing requests."""
    
    ALLOWED_EXTENSIONS = {'pdf'}
    
    def __init__(self, session_type_service: SessionTypeService):
        """
        Initialize the validator.
        
        Args:
            session_type_service: Service for session type operations
        """
        self.session_type_service = session_type_service
    
    @staticmethod
    def _allowed_file(filename: str) -> bool:
        """Check if the file has an allowed extension.
        
        Args:
            filename: The filename to check
            
        Returns:
            True if the file extension is allowed, False otherwise
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in SessionRequestValidator.ALLOWED_EXTENSIONS
    
    def validate_parse_request(self, request: Request) -> ValidationResult:
        """
        Validate a session parse request.
        
        Args:
            request: Flask request object
            
        Returns:
            ValidationResult with validated data or error
        """
        # Check if file is present in request
        if 'file' not in request.files:
            return ValidationResult(
                success=False,
                error=ValidationError('No file provided', 400)
            )
        
        file: FileStorage = request.files['file']
        
        # Check if file was selected
        if file.filename == '' or file.filename is None:
            return ValidationResult(
                success=False,
                error=ValidationError('No file selected', 400)
            )
        
        # Validate file extension
        if not self._allowed_file(file.filename):
            return ValidationResult(
                success=False,
                error=ValidationError('Invalid file type. Only PDF files are allowed.', 400)
            )
        
        # Get optional parameters
        session_date_str = request.form.get('date')
        session_type_param = request.form.get('session_type')
        debug = request.form.get('debug', 'false').lower() == 'true'
        force = request.form.get('force', 'false').lower() == 'true'
        topic = request.form.get('topic')
        
        # Try to parse filename for date and session type
        filename_date, filename_session_type = FileUtils.parse_session_filename(file.filename)
        
        # Parse date if provided, otherwise use filename-parsed date
        date_obj: Optional[date] = None
        if session_date_str:
            try:
                date_obj = datetime.strptime(session_date_str, '%Y-%m-%d').date()
            except ValueError:
                return ValidationResult(
                    success=False,
                    error=ValidationError('Invalid date format. Use YYYY-MM-DD.', 400)
                )
        elif filename_date:
            date_obj = filename_date.date()
        
        # Use session_type parameter if provided, otherwise use filename-parsed type
        session_type_short = session_type_param or filename_session_type
        
        # Get session type ID if short name is provided
        session_type_id: Optional[int] = None
        if session_type_short:
            session_type_id = self.session_type_service.get_id_by_short_name(session_type_short)
            if session_type_id is None:
                return ValidationResult(
                    success=False,
                    error=ValidationError(f'Invalid session type: {session_type_short}', 400)
                )
        
        # Return validated data
        return ValidationResult(
            success=True,
            data={
                'file': file,
                'date': date_obj,
                'session_type_id': session_type_id,
                'debug': debug,
                'force': force,
                'topic': topic
            }
        )
