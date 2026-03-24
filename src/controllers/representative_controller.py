"""Representative controller for handling HTTP requests for representative data."""
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from uuid import UUID
from src.service.postgres_service import PostgreService
from src.service.representative_service import RepresentativeService
from src.service.intervention_service import InterventionService
from src.service.province_service import ProvinceService
from src.service.party_service import PartyService
from src.service.coalition_service import CoalitionService
from src.service.topic_service import TopicService
from src.service.senate_session_service import SenateSessionService
from src.service.representative_topic_summary_service import RepresentativeTopicSummaryService
from src.dto.models.intervention import Intervention
from src.filters.representative_filter import RepresentativeFilter
from sqlalchemy import and_, or_
from src.dto.models.attendance_session import AttendanceSession
from src.dto.models.topic import Topic
from src.dto.models.senate_session import SenateSession
from src.dto.models.representative_topic_summary import RepresentativeTopicSummary
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
    representative_service = RepresentativeService(postgres_service)
    intervention_service = InterventionService(postgres_service)
    province_service = ProvinceService(postgres_service)
    party_service = PartyService(postgres_service)
    coalition_service = CoalitionService(postgres_service)
    topic_service = TopicService(postgres_service)
    senate_session_service = SenateSessionService(postgres_service)
    representative_topic_summary_service = RepresentativeTopicSummaryService(postgres_service)
    representative_filter = RepresentativeFilter(province_service, party_service, coalition_service)
    
    @app.before_request
    def log_request():
        """Log all incoming requests."""
        print(f"Incoming request: {request.method} {request.path}")
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'representative-api'}), 200
    
    @app.route('/api/representatives', methods=['GET'])
    def get_all_representatives():
        """
        Get all representatives.
        
        Query parameters:
            province: Optional filter by province name
            party: Optional filter by party name
            coalition: Optional filter by coalition name
            
        Returns:
            JSON response with list of representatives
        """
        try:
            province = request.args.get('province')
            party = request.args.get('party')
            coalition = request.args.get('coalition')
            
            # Get all representatives
            representatives = representative_service.get_all()
            
            # Apply filters using filter class
            filtered_reps = representative_filter.filter_representatives(
                representatives=representatives,
                province=province,
                party=party,
                coalition=coalition
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'representatives': filtered_reps,
                    'total': len(filtered_reps)
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve representatives'
            }), 500
    
    @app.route('/api/representatives/<representative_id>/sessions', methods=['GET'])
    def get_representative_sessions(representative_id: str):
        """
        Get all senate sessions where a representative participated.
        
        Args:
            representative_id: UUID of the representative
            
        Returns:
            JSON response with list of senate sessions
        """
        try:
            # Convert string UUID to UUID object
            rep_uuid = UUID(representative_id)
            

            
            with postgres_service.session_scope() as session:
                # Query for distinct sessions where representative participated
                sessions_query = session.query(SenateSession).join(
                    AttendanceSession,
                    SenateSession.UniqueID == AttendanceSession.SenateSession_id
                ).filter(
                    AttendanceSession.Representative_id == rep_uuid
                ).distinct()
                
                # Also get sessions where representative had interventions
                intervention_sessions = session.query(SenateSession).join(
                    Topic,
                    SenateSession.UniqueID == Topic.SenateSession_id
                ).join(
                    Intervention,
                    Topic.UniqueID == Intervention.Topic_id
                ).filter(
                    Intervention.Representative_id == rep_uuid
                ).distinct()
                
                # Combine and get unique sessions
                all_sessions = set()
                for s in sessions_query.all():
                    all_sessions.add((s.UniqueID, s.Date))
                for s in intervention_sessions.all():
                    all_sessions.add((s.UniqueID, s.Date))
                
                # Sort by date descending
                sorted_sessions = sorted(all_sessions, key=lambda x: x[1], reverse=True)
            
            sessions = []
            for session_id, session_date in sorted_sessions:
                sessions.append({
                    'session_id': session_id,
                    'date': session_date.isoformat()
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'representative_id': representative_id,
                    'sessions': sessions,
                    'total': len(sessions)
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve representative sessions'
            }), 500
    
    @app.route('/api/representatives/<representative_id>/topics', methods=['GET'])
    def get_representative_topics(representative_id: str):
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
            
            # Debug logging
            print(f"DEBUG: representative_id={representative_id}, session_id={session_id}")
            
            with postgres_service.session_scope() as session:
                query = session.query(
                    Topic.UniqueID,
                    Topic.Name,
                    Topic.SenateSession_id,
                    SenateSession.Date,
                    func.count(Intervention.UniqueID).label('intervention_count'),
                    RepresentativeTopicSummary.Summary
                ).join(
                    SenateSession,
                    Topic.SenateSession_id == SenateSession.UniqueID
                ).join(
                    Intervention,
                    Topic.UniqueID == Intervention.Topic_id
                ).outerjoin(
                    RepresentativeTopicSummary,
                    and_(
                        RepresentativeTopicSummary.Topic_id == Topic.UniqueID,
                        RepresentativeTopicSummary.Representative_id == rep_uuid
                    )
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
                    SenateSession.Date,
                    RepresentativeTopicSummary.Summary
                )
                
                result = query.all()
            
            topics = []
            for row in result:
                topics.append({
                    'topic_id': row[0],
                    'name': row[1],
                    'session_id': row[2],
                    'session_date': row[3].isoformat(),
                    'intervention_count': row[4],
                    'summary': row[5]
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
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve representative topics'
            }), 500
    
    @app.route('/api/representatives/<representative_id>/topics/<int:topic_id>/interventions', methods=['GET'])
    def get_representative_topic_interventions(representative_id: str, topic_id: int):
        """
        Get all interventions for a specific topic from a representative.
        
        Args:
            representative_id: UUID of the representative
            topic_id: ID of the topic
            
        Returns:
            JSON response with list of interventions
        """
        try:
            # Convert string UUID to UUID object
            rep_uuid = UUID(representative_id)
            
            # Get representative info
            representative = representative_service.get_by_id(rep_uuid)
            if not representative:
                return jsonify({
                    'success': False,
                    'error': 'Representative not found'
                }), 404
            
            # Get topic info using service
            topic = topic_service.get_by_id(topic_id)
            if not topic:
                return jsonify({
                    'success': False,
                    'error': 'Topic not found'
                }), 404
            
            # Get interventions for the topic
            rep_interventions = intervention_service.get_by_topic_and_representative(topic_id, rep_uuid)

            # Get summary for representative-topic pair
            rep_topic_summary = representative_topic_summary_service.get_by_representative_and_topic(
                rep_uuid,
                topic_id
            )
            
            # Get session info
            session_id = getattr(topic, 'SenateSession_id', 0)
            session = senate_session_service.get_by_id(session_id)
            
            interventions_data = []
            for intervention in rep_interventions:
                interventions_data.append({
                    'intervention_id': intervention.UniqueID,
                    'text': intervention.Text,
                    'role': intervention.Role,
                    'order': intervention.Intervention_order
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'representative': {
                        'id': representative_id,
                        'full_name': representative.Full_name,
                        'last_name': representative.Last_name,
                        'first_name': representative.First_name
                    },
                    'topic': {
                        'id': topic_id,
                        'name': topic.Name,
                        'session_id': topic.SenateSession_id,
                        'session_date': session.Date.isoformat()
                    },
                    'summary': rep_topic_summary.Summary if rep_topic_summary else None,
                    'interventions': interventions_data,
                    'total': len(interventions_data)
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve interventions'
            }), 500
    
    return app


if __name__ == '__main__':
    """Run the Flask application in development mode."""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5002)
