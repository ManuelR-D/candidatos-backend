"""
Example script to run the Flask API server for session parsing and representative queries.

This script starts a Flask web server that exposes endpoints for parsing
legislative session PDFs and querying representative data.
"""

from flask import Flask
from flask_cors import CORS
import os
from src.controllers import session_controller, representative_controller, topic_controller

import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def create_combined_app(db_config=None):
    """
    Create a combined Flask app with routes from both controllers.
    
    Args:
        db_config: Optional database configuration
        
    Returns:
        Combined Flask application
    """
    # Create apps from all controllers
    session_app = session_controller.create_app(db_config)
    rep_app = representative_controller.create_app(db_config)
    topic_app = topic_controller.create_app(db_config)
    
    # Create a new master app
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.config.update(session_app.config)
    
    # Register all routes from session_app
    for rule in session_app.url_map.iter_rules():
        if rule.endpoint != 'static' and rule.methods is not None:
            view_func = session_app.view_functions[rule.endpoint]
            app.add_url_rule(
                rule.rule,
                endpoint=f'session_{rule.endpoint}',
                view_func=view_func,
                methods=rule.methods - {'HEAD', 'OPTIONS'}
            )
    
    # Register all routes from rep_app (except duplicate /health)
    for rule in rep_app.url_map.iter_rules():
        if rule.endpoint != 'static' and rule.rule != '/health' and rule.methods is not None:
            view_func = rep_app.view_functions[rule.endpoint]
            app.add_url_rule(
                rule.rule,
                endpoint=f'rep_{rule.endpoint}',
                view_func=view_func,
                methods=rule.methods - {'HEAD', 'OPTIONS'}
            )
    
    # Register all routes from topic_app (except duplicate /health)
    for rule in topic_app.url_map.iter_rules():
        if rule.endpoint != 'static' and rule.rule != '/health' and rule.methods is not None:
            view_func = topic_app.view_functions[rule.endpoint]
            app.add_url_rule(
                rule.rule,
                endpoint=f'topic_{rule.endpoint}',
                view_func=view_func,
                methods=rule.methods - {'HEAD', 'OPTIONS'}
            )
    
    return app


if __name__ == '__main__':
    # Optional: Configure database connection via environment variables
    # export DB_HOST=localhost
    # export DB_PORT=5433
    # export DB_NAME=senate_db
    # export DB_USER=senate_user
    # export DB_PASSWORD=senate_pass
    
    # Create the combined Flask app
    try:
        app = create_combined_app()
        
        # Debug: Print registered routes
        print("Registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.methods} {rule.rule}")
        print()
    except Exception as e:
        print(f"Error creating app: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    # Run the server
    print("Starting Combined API server...")
    print("\nSession Parser endpoints:")
    print("  GET  /health                                                     - Health check")
    print("  POST /api/sessions/parse                                         - Parse and store a session PDF")
    print("  GET  /api/sessions                                               - Get all sessions (placeholder)")
    print("\nRepresentative Query endpoints:")
    print("  GET  /api/representatives                                        - Get all representatives")
    print("  GET  /api/representatives/<id>/sessions                          - Get all sessions for representative")
    print("  GET  /api/representatives/<id>/topics                            - Get all topics for representative")
    print("  GET  /api/representatives/<id>/topics/<topic_id>/interventions   - Get interventions by topic")
    print("\nTopic Query endpoints:")
    print("  GET  /api/topics/by-representative/<id>                          - Get all topics for representative")
    print("  GET  /api/topics/<topic_id>                                      - Get topic by ID")
    print("  GET  /api/topics                                                 - Get all topics")
    print(f"\nServer running on http://localhost:{os.getenv('PORT', 5101)}")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5101))
    )
