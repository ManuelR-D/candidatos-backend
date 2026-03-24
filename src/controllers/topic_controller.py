"""Topic controller for handling HTTP requests for topic data."""
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from uuid import UUID
from src.service.postgres_service import PostgreService
from src.service.topic_service import TopicService
from src.dto.models.topic import Topic
from src.dto.models.intervention import Intervention
from src.dto.models.senate_session import SenateSession
from src.dto.models.representative import Representative
from sqlalchemy import func


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
    topic_service = TopicService(postgres_service)
    
    @app.before_request
    def log_request():
        """Log all incoming requests."""
        print(f"Incoming request: {request.method} {request.path}")
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'topic-controller'}), 200
    
    @app.route('/api/topics/by-representative/<representative_id>', methods=['GET'])
    def get_all_by_representative(representative_id: str):
        """
        Get all topics where a representative has interventions.
        
        Args:
            representative_id: UUID of the representative
            
        Query parameters:
            session_id: Optional filter by senate session ID
            
        Returns:
            JSON response with list of topics
        """
        try:
            session_id = request.args.get('session_id', type=int)
            rep_uuid = UUID(representative_id)
            
            print(f"Getting topics for representative: {representative_id}, session_id={session_id}")
            
            with postgres_service.session_scope() as session:
                query = session.query(
                    Topic.UniqueID,
                    Topic.Name,
                    Topic.SenateSession_id,
                    SenateSession.Date,
                    func.count(Intervention.UniqueID).label('intervention_count')
                ).join(
                    SenateSession,
                    Topic.SenateSession_id == SenateSession.UniqueID
                ).join(
                    Intervention,
                    Topic.UniqueID == Intervention.Topic_id
                ).filter(
                    Intervention.Representative_id == rep_uuid
                )
                
                if session_id:
                    query = query.filter(Topic.SenateSession_id == session_id)
                    query = query.order_by(Topic.UniqueID)
                else:
                    query = query.order_by(SenateSession.Date.desc(), Topic.UniqueID)
                
                query = query.group_by(
                    Topic.UniqueID,
                    Topic.Name,
                    Topic.SenateSession_id,
                    SenateSession.Date
                )
                
                result = query.all()
            
            topics = []
            for row in result:
                topics.append({
                    'topic_id': row[0],
                    'name': row[1],
                    'session_id': row[2],
                    'session_date': row[3].isoformat() if row[3] else None,
                    'intervention_count': row[4]
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'representative_id': representative_id,
                    'session_id': session_id,
                    'topics': topics,
                    'total': len(topics)
                }
            }), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid UUID format',
                'message': str(e)
            }), 400
        except Exception as e:
            print(f"Error in get_all_by_representative: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve topics for representative'
            }), 500
    
    @app.route('/api/topics/<int:topic_id>', methods=['GET'])
    def get_topic_by_id(topic_id: int):
        """
        Get a topic by its ID.
        
        Args:
            topic_id: Unique ID of the topic
            
        Returns:
            JSON response with topic details
        """
        try:
            topic = topic_service.get_by_id(topic_id)
            
            if not topic:
                return jsonify({
                    'success': False,
                    'message': 'Topic not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': topic.to_dict()
            }), 200
            
        except Exception as e:
            print(f"Error in get_topic_by_id: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve topic'
            }), 500
    
    @app.route('/api/topics', methods=['GET'])
    def get_all_topics():
        """
        Get all topics with optional filtering.
        
        Query parameters:
            session_id: Optional filter by senate session ID
            
        Returns:
            JSON response with list of topics
        """
        try:
            session_id = request.args.get('session_id', type=int)
            
            with postgres_service.session_scope() as session:
                query = session.query(
                    Topic.UniqueID,
                    Topic.Name,
                    Topic.SenateSession_id,
                    SenateSession.Date,
                    func.count(Intervention.UniqueID).label('intervention_count')
                ).join(
                    SenateSession,
                    Topic.SenateSession_id == SenateSession.UniqueID
                ).outerjoin(
                    Intervention,
                    Topic.UniqueID == Intervention.Topic_id
                )

                if session_id:
                    query = query.filter(Topic.SenateSession_id == session_id)
                    query = query.order_by(Topic.UniqueID)
                else:
                    query = query.order_by(SenateSession.Date.desc(), Topic.UniqueID)

                query = query.group_by(
                    Topic.UniqueID,
                    Topic.Name,
                    Topic.SenateSession_id,
                    SenateSession.Date
                )

                result = query.all()

            topics_list = []
            for row in result:
                topics_list.append({
                    'topic_id': row[0],
                    'name': row[1],
                    'session_id': row[2],
                    'session_date': row[3].isoformat() if row[3] else None,
                    'intervention_count': row[4]
                })

            return jsonify({
                'success': True,
                'data': {
                    'topics': topics_list,
                    'total': len(topics_list)
                }
            }), 200
            
        except Exception as e:
            print(f"Error in get_all_topics: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve topics'
            }), 500

    @app.route('/api/topics/<int:topic_id>/representatives', methods=['GET'])
    def get_representatives_by_topic(topic_id: int):
        """
        Get all representatives that have interventions in a given topic.

        Args:
            topic_id: Unique ID of the topic

        Returns:
            JSON response with list of representatives
        """
        try:
            with postgres_service.session_scope() as session:
                topic_row = session.query(
                    Topic.UniqueID,
                    Topic.Name,
                    Topic.SenateSession_id,
                    SenateSession.Date
                ).join(
                    SenateSession,
                    Topic.SenateSession_id == SenateSession.UniqueID
                ).filter(
                    Topic.UniqueID == topic_id
                ).first()

                if not topic_row:
                    return jsonify({
                        'success': False,
                        'message': 'Topic not found'
                    }), 404

                reps_query = session.query(
                    Representative.UniqueID,
                    Representative.Full_name,
                    Representative.First_name,
                    Representative.Last_name,
                    Representative.Party_id,
                    Representative.Province_id,
                    Representative.Coalition_id,
                    Representative.Photo_url,
                    func.count(Intervention.UniqueID).label('intervention_count')
                ).join(
                    Intervention,
                    Representative.UniqueID == Intervention.Representative_id
                ).filter(
                    Intervention.Topic_id == topic_id
                ).group_by(
                    Representative.UniqueID,
                    Representative.Full_name,
                    Representative.First_name,
                    Representative.Last_name,
                    Representative.Party_id,
                    Representative.Province_id,
                    Representative.Coalition_id,
                    Representative.Photo_url
                ).order_by(
                    Representative.Last_name,
                    Representative.First_name
                )

                reps_result = reps_query.all()

            representatives = []
            for row in reps_result:
                representatives.append({
                    'id': str(row[0]),
                    'full_name': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'party_id': row[4],
                    'province_id': row[5],
                    'coalition_id': row[6],
                    'photo_url': row[7],
                    'intervention_count': row[8]
                })

            return jsonify({
                'success': True,
                'data': {
                    'topic': {
                        'id': topic_row[0],
                        'name': topic_row[1],
                        'session_id': topic_row[2],
                        'session_date': topic_row[3].isoformat() if topic_row[3] else None
                    },
                    'representatives': representatives,
                    'total': len(representatives)
                }
            }), 200

        except Exception as e:
            print(f"Error in get_representatives_by_topic: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve representatives for topic'
            }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=True)
