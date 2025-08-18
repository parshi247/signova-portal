from flask import Blueprint, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime, timedelta

signova_api_bp = Blueprint('signova_api', __name__)

# Enable CORS for all routes in this blueprint
CORS(signova_api_bp, origins=['http://157.230.85.71', 'https://signova.ai', 'https://mobile.signova.ai'])

# Mock user data - in production this would come from database
MOCK_USERS = {
    'test@signova.ai': {
        'id': 1,
        'email': 'test@signova.ai',
        'name': 'Test User',
        'plan': 'Professional',
        'documents_created': 23,
        'documents_sent': 18,
        'completed': 15,
        'pending': 3,
        'active_profiles': 5
    },
    'demo@signova.ai': {
        'id': 2,
        'email': 'demo@signova.ai', 
        'name': 'Demo User',
        'plan': 'Business',
        'documents_created': 47,
        'documents_sent': 42,
        'completed': 38,
        'pending': 4,
        'active_profiles': 8
    }
}

def get_user_by_email(email):
    """Get user data by email, return real user data or zeros for new users"""
    # Check if user exists in our mock database
    if email in MOCK_USERS:
        return MOCK_USERS[email]
    
    # For new/unknown users, return zero metrics (real user experience)
    return {
        'id': 999,
        'email': email,
        'name': 'New User',
        'plan': 'Starter',
        'documents_created': 0,
        'documents_sent': 0,
        'completed': 0,
        'pending': 0,
        'active_profiles': 0  # New users start with 0 profiles
    }

@signova_api_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get user analytics/dashboard data"""
    # In production, get user from authentication
    user_email = request.args.get('email', 'demo@signova.ai')
    user_data = get_user_by_email(user_email)
    
    analytics_data = {
        'documents_created': user_data['documents_created'],
        'documents_sent': user_data['documents_sent'],
        'completed': user_data['completed'],
        'pending': user_data['pending'],
        'active_profiles': user_data['active_profiles'],
        'document_types': 617,  # System-wide metric
        'success_rate': round((user_data['completed'] / max(user_data['documents_sent'], 1)) * 100, 1),
        'last_updated': datetime.now().isoformat()
    }
    
    return jsonify(analytics_data)

@signova_api_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """Get user profiles"""
    user_email = request.args.get('email', 'demo@signova.ai')
    user_data = get_user_by_email(user_email)
    
    # Mock profile data
    profiles = {
        'personal': {
            'id': 1,
            'name': 'Personal Profile',
            'type': 'individual',
            'documents_count': user_data['documents_created'] // 2,
            'last_used': (datetime.now() - timedelta(days=1)).isoformat()
        },
        'business': {
            'id': 2,
            'name': 'Business Profile', 
            'type': 'company',
            'documents_count': user_data['documents_created'] // 2,
            'last_used': datetime.now().isoformat()
        }
    }
    
    return jsonify(profiles)

@signova_api_bp.route('/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get user's recent activity"""
    user_email = request.args.get('email', 'demo@signova.ai')
    user_data = get_user_by_email(user_email)
    
    # If user has no documents, return empty activity
    if user_data['documents_created'] == 0:
        return jsonify({'activities': []})
    
    # Generate mock recent activities for users with documents
    activities = []
    activity_types = ['created', 'sent', 'signed', 'completed', 'viewed']
    document_types = ['Contract', 'Invoice', 'Proposal', 'Agreement', 'Report']
    
    # Limit activities to actual document count
    activity_count = min(user_data['documents_created'], 5)
    
    for i in range(activity_count):
        activity = {
            'id': i + 1,
            'type': random.choice(activity_types),
            'document': f"{random.choice(document_types)} #{random.randint(1000, 9999)}",
            'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            'status': random.choice(['completed', 'pending', 'in_progress'])
        }
        activities.append(activity)
    
    return jsonify({'activities': activities})

@signova_api_bp.route('/ai-suggestions', methods=['GET'])
def get_ai_suggestions():
    """Get AI suggestions for user"""
    user_email = request.args.get('email', 'demo@signova.ai')
    user_data = get_user_by_email(user_email)
    
    # Different suggestions for new users vs experienced users
    if user_data['documents_created'] == 0:
        # Suggestions for new users
        suggestions = [
            {
                'id': 1,
                'type': 'onboarding',
                'title': 'Create Your First Document',
                'description': 'Get started by creating your first contract, invoice, or proposal using our AI-powered templates.',
                'priority': 'high',
                'action': 'create_first_document'
            },
            {
                'id': 2,
                'type': 'setup',
                'title': 'Set Up Your Profile',
                'description': 'Complete your profile to enable AI auto-fill for faster document creation.',
                'priority': 'medium',
                'action': 'setup_profile'
            },
            {
                'id': 3,
                'type': 'tutorial',
                'title': 'Take the Quick Tour',
                'description': 'Learn how to maximize your productivity with our 2-minute guided tour.',
                'priority': 'low',
                'action': 'start_tutorial'
            }
        ]
    else:
        # Suggestions for experienced users
        success_rate = round((user_data['completed'] / max(user_data['documents_sent'], 1)) * 100, 1)
        suggestions = [
            {
                'id': 1,
                'type': 'optimization',
                'title': 'Optimize Document Templates',
                'description': f'Based on your {user_data["documents_created"]} documents, we suggest creating reusable templates.',
                'priority': 'high',
                'action': 'create_template'
            },
            {
                'id': 2,
                'type': 'automation',
                'title': 'Set Up Auto-Reminders',
                'description': f'You have {user_data["pending"]} pending documents. Auto-reminders can improve completion rates.',
                'priority': 'medium',
                'action': 'setup_reminders'
            },
            {
                'id': 3,
                'type': 'analytics',
                'title': 'Review Performance Metrics',
                'description': f'Your {success_rate}% completion rate is {"above" if success_rate > 80 else "below"} average. See detailed insights.',
                'priority': 'low',
                'action': 'view_analytics'
            }
        ]
    
    return jsonify({'suggestions': suggestions})

@signova_api_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get user documents"""
    user_email = request.args.get('email', 'demo@signova.ai')
    user_data = get_user_by_email(user_email)
    
    # Generate mock documents
    documents = []
    document_types = ['Contract', 'Invoice', 'Proposal', 'Agreement', 'Report']
    statuses = ['draft', 'sent', 'signed', 'completed']
    
    for i in range(min(user_data['documents_created'], 10)):
        doc = {
            'id': i + 1,
            'title': f"{random.choice(document_types)} #{random.randint(1000, 9999)}",
            'type': random.choice(document_types).lower(),
            'status': random.choice(statuses),
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            'updated_at': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        }
        documents.append(doc)
    
    return jsonify({'documents': documents})

@signova_api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Signova API Backend',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


# Additional endpoints that the portal might be calling

@signova_api_bp.route('/documents/<int:doc_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_document(doc_id):
    """Handle individual document operations"""
    if request.method == 'GET':
        # Get specific document
        return jsonify({
            'id': doc_id,
            'title': f'Document #{doc_id}',
            'type': 'contract',
            'status': 'draft',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })
    elif request.method == 'PUT':
        # Update document
        return jsonify({'message': f'Document {doc_id} updated successfully'})
    elif request.method == 'DELETE':
        # Delete document
        return jsonify({'message': f'Document {doc_id} deleted successfully'})

@signova_api_bp.route('/profiles/<int:profile_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_profile(profile_id):
    """Handle individual profile operations"""
    if request.method == 'GET':
        # Get specific profile
        return jsonify({
            'id': profile_id,
            'name': f'Profile #{profile_id}',
            'type': 'business',
            'documents_count': 5,
            'last_used': datetime.now().isoformat()
        })
    elif request.method == 'PUT':
        # Update profile
        return jsonify({'message': f'Profile {profile_id} updated successfully'})
    elif request.method == 'DELETE':
        # Delete profile
        return jsonify({'message': f'Profile {profile_id} deleted successfully'})

@signova_api_bp.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    """Handle message operations"""
    if request.method == 'GET':
        # Get messages
        return jsonify({
            'messages': [
                {
                    'id': 1,
                    'subject': 'Document signed',
                    'content': 'Your contract has been signed',
                    'timestamp': datetime.now().isoformat(),
                    'read': False
                }
            ]
        })
    elif request.method == 'POST':
        # Send message
        return jsonify({'message': 'Message sent successfully'})

@signova_api_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data - alternative endpoint"""
    user_email = request.args.get('email', 'demo@signova.ai')
    user_data = get_user_by_email(user_email)
    
    return jsonify({
        'user': user_data,
        'analytics': {
            'documents_created': user_data['documents_created'],
            'documents_sent': user_data['documents_sent'],
            'completed': user_data['completed'],
            'pending': user_data['pending'],
            'active_profiles': user_data['active_profiles'],
            'success_rate': round((user_data['completed'] / max(user_data['documents_sent'], 1)) * 100, 1)
        },
        'last_updated': datetime.now().isoformat()
    })

@signova_api_bp.route('/create-document', methods=['POST'])
def create_document():
    """Create a new document"""
    data = request.get_json() or {}
    doc_type = data.get('type', 'contract')
    
    return jsonify({
        'id': random.randint(1000, 9999),
        'type': doc_type,
        'title': f'New {doc_type.title()} #{random.randint(1000, 9999)}',
        'status': 'draft',
        'created_at': datetime.now().isoformat(),
        'message': f'{doc_type.title()} created successfully'
    })

@signova_api_bp.route('/bulk-operations', methods=['POST'])
def bulk_operations():
    """Handle bulk operations"""
    data = request.get_json() or {}
    operation = data.get('operation', 'unknown')
    
    return jsonify({
        'operation': operation,
        'status': 'completed',
        'message': f'Bulk {operation} completed successfully',
        'processed_count': random.randint(1, 10)
    })

# Catch-all route for any missing endpoints
@signova_api_bp.route('/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(endpoint):
    """Catch-all for any missing endpoints"""
    return jsonify({
        'endpoint': endpoint,
        'method': request.method,
        'message': f'Endpoint /{endpoint} is not implemented yet',
        'status': 'placeholder'
    }), 501  # Not Implemented

