"""
AI Avatar API Routes

Flask blueprint containing all API endpoints exactly as specified in the Technical Design Document.
Includes authentication, chat, avatar configuration, and conversation management.
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session, send_file, make_response, redirect
from werkzeug.utils import secure_filename

from src.auth.auth_manager import authenticate_user, is_authenticated, clear_session
from src.input.input_processor import InputProcessor
from src.llm.openai_service import OpenAIService
from src.avatar.avatar_manager import AvatarManager
from src.speech.azure_speech import AzureSpeechService

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
try:
    speech_service = AzureSpeechService()
    input_processor = InputProcessor(speech_service)
    openai_service = OpenAIService()
    avatar_manager = AvatarManager()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    # Create placeholder services for development
    speech_service = None
    input_processor = None
    openai_service = None
    avatar_manager = AvatarManager()

# Authentication endpoints as specified in TDD
@api_bp.route('/login', methods=['POST'])
def login():
    """
    Handle user authentication as specified in TDD.
    Credentials: UTASAvatar / UTASRocks!
    """
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        if authenticate_user(username, password):
            session['authenticated'] = True
            session['username'] = username
            session['login_time'] = datetime.utcnow().isoformat()
            
            logger.info(f"User '{username}' logged in successfully")
            return jsonify({'success': True, 'redirect': '/chat'})
        else:
            logger.warning(f"Failed login attempt for user '{username}'")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@api_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout as specified in TDD"""
    try:
        username = session.get('username', 'unknown')
        clear_session(session)
        logger.info(f"User '{username}' logged out")
        return jsonify({'success': True, 'redirect': '/login'})
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Main chat endpoint as specified in TDD
@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint handling both text and voice inputs as specified in TDD.
    """
    if not is_authenticated(session):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        input_type = request.form.get('input_type', 'text')
        model = request.form.get('model', 'gpt4o')
        conversation_history = json.loads(request.form.get('conversation_history', '[]'))
        avatar_settings = json.loads(request.form.get('avatar_settings', '{}'))
        
        # Process input based on type
        if input_type == 'voice':
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio']
            audio_data = audio_file.read()
            
            if not input_processor:
                return jsonify({'error': 'Speech service not available'}), 503
                
            # Process voice input with Azure Speech Service
            import asyncio
            try:
                # Run async transcription
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                processed_input = loop.run_until_complete(
                    input_processor.process_voice_input(audio_data)
                )
                loop.close()
            except Exception as e:
                logger.error(f"Voice processing error: {str(e)}")
                processed_input = {
                    'text': '',
                    'confidence': 0.0,
                    'input_type': 'voice',
                    'success': False,
                    'error': f'Voice processing failed: {str(e)}'
                }
        
        elif input_type == 'text':
            text = request.form.get('text')
            if not text:
                return jsonify({'error': 'No text provided'}), 400
            
            if not input_processor:
                # Fallback text processing
                processed_input = {
                    'text': text.strip(),
                    'confidence': 1.0,
                    'input_type': 'text',
                    'success': True,
                    'error': None
                }
            else:
                processed_input = input_processor.process_text_input(text)
        
        else:
            return jsonify({'error': 'Invalid input type'}), 400
        
        if not processed_input['success']:
            return jsonify({'error': processed_input['error']}), 400
        
        # Get AI response
        if not openai_service:
            ai_response = {
                'content': f"Echo: {processed_input['text']} (OpenAI service not available)",
                'model_used': model,
                'tokens_used': 0,
                'success': True
            }
        else:
            ai_response = openai_service.get_ai_response(
                processed_input['text'], 
                model, 
                conversation_history
            )
        
        # Generate avatar video with user settings
        try:
            # Use asyncio to run the avatar generation
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            avatar_video = loop.run_until_complete(
                avatar_manager.create_avatar_video(
                    ai_response['content'], 
                    avatar_settings
                )
            )
            loop.close()
        except Exception as e:
            logger.warning(f"Avatar video generation failed: {str(e)}")
            # Return error instead of demo video fallback
            avatar_video = {
                'video_id': None,
                'config_used': avatar_settings,
                'success': False,
                'error': str(e)
            }
        
        # Store conversation in session
        if 'conversation' not in session:
            session['conversation'] = []
        
        session['conversation'].extend([
            {
                'role': 'user', 
                'content': processed_input['text'],
                'input_type': input_type,
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'role': 'assistant', 
                'content': ai_response['content'],
                'model_used': model,
                'tokens_used': ai_response.get('tokens_used', 0),
                'avatar_config': avatar_video.get('config_used', {}),
                'timestamp': datetime.utcnow().isoformat()
            }
        ])
        
        # Get direct Azure Blob Storage URL instead of using redirect
        direct_video_url = None
        if avatar_video.get('video_id'):
            direct_video_url = avatar_manager.get_video_path(avatar_video['video_id'])
            # If it's not a direct URL, fallback to the redirect endpoint
            if not direct_video_url or not direct_video_url.startswith('http'):
                direct_video_url = f'/api/video/{avatar_video["video_id"]}'
        
        response = {
            'text': ai_response['content'],
            'model': model,
            'input_type': input_type,
            'confidence': processed_input['confidence'],
            'tokens_used': ai_response.get('tokens_used', 0),
            'video_url': direct_video_url,
            'avatar_config': avatar_video.get('config_used', {}),
            'user_input_text': processed_input['text'],  # Include the actual processed text
            'success': True
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Model management as specified in TDD
@api_bp.route('/models', methods=['GET'])
def get_models():
    """Get available AI models as specified in TDD"""
    if not is_authenticated(session):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        if openai_service:
            models = openai_service.get_available_models()
        else:
            models = ['gpt4o', 'o3-mini']  # Fallback
        
        return jsonify({'models': models})
        
    except Exception as e:
        logger.error(f"Get models error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Avatar configuration endpoints as specified in TDD
@api_bp.route('/avatar/config', methods=['GET', 'POST'])
def avatar_config():
    """Get or update avatar configuration as specified in TDD"""
    if not is_authenticated(session):
        return jsonify({'error': 'Not authenticated'}), 401
    
    if request.method == 'GET':
        try:
            # Return available avatar options and current settings
            options = avatar_manager.get_avatar_options()
            current_settings = session.get('avatar_config', avatar_manager.default_config)
            
            return jsonify({
                'available_options': options,
                'current_settings': current_settings
            })
            
        except Exception as e:
            logger.error(f"Get avatar config error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    elif request.method == 'POST':
        try:
            config = request.get_json()
            
            if not config:
                return jsonify({'error': 'No configuration provided'}), 400
            
            # Validate configuration
            if not avatar_manager.validate_config(config):
                return jsonify({'error': 'Invalid avatar configuration'}), 400
            
            # Store in session
            session['avatar_config'] = config
            
            # Test avatar with new settings (optional preview)
            if config.get('preview'):
                # Use synchronous processing for now
                preview_video = {
                    'video_id': 'preview-video-123',
                    'success': True
                }
                return jsonify({
                    'success': True,
                    'config': config,
                    'preview_url': f'/api/video/{preview_video["video_id"]}' if preview_video.get('video_id') else None
                })
            
            return jsonify({'success': True, 'config': config})
            
        except Exception as e:
            logger.error(f"Update avatar config error: {str(e)}")
            return jsonify({'error': 'Failed to update avatar configuration'}), 500

# Video serving endpoint as specified in TDD
@api_bp.route('/video/<video_id>', methods=['GET', 'HEAD', 'OPTIONS'])
def get_video(video_id):
    """Serve generated avatar videos as specified in TDD"""
    # Handle OPTIONS requests for CORS preflight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = (
            'Content-Type, Accept'
        )
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    if not is_authenticated(session):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        video_path = avatar_manager.get_video_path(video_id)
        if not video_path:
            return jsonify({'error': 'Video not found'}), 404
        
        # Check if it's a URL (Azure Blob Storage) or local path
        if video_path.startswith('http'):
            # Redirect to Azure Blob Storage URL with proper CORS headers
            response = make_response(redirect(video_path))
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = (
                'GET, HEAD, OPTIONS'
            )
            response.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Accept'
            )
            response.headers['Access-Control-Expose-Headers'] = (
                'Location, Content-Type, Content-Length'
            )
            
            logger.info(
                f"Redirecting video {video_id} to Azure Blob Storage: "
                f"{video_path}"
            )
            return response
        else:
            # Serve local file
            if not os.path.exists(video_path):
                return jsonify({'error': 'Video file not found'}), 404
            
            response = make_response(
                send_file(video_path, mimetype='video/mp4')
            )
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = (
                'GET, HEAD, OPTIONS'
            )
            response.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Accept'
            )
            return response
        
    except Exception as e:
        logger.error(f"Video serving error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Conversation management as specified in TDD
@api_bp.route('/conversation', methods=['GET', 'DELETE'])
def conversation_management():
    """Get or clear conversation history as specified in TDD"""
    if not is_authenticated(session):
        return jsonify({'error': 'Not authenticated'}), 401
    
    if request.method == 'GET':
        try:
            conversation = session.get('conversation', [])
            return jsonify({'conversation': conversation})
            
        except Exception as e:
            logger.error(f"Get conversation error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    elif request.method == 'DELETE':
        try:
            session['conversation'] = []
            logger.info(
                f"Conversation cleared for user {session.get('username')}"
            )
            return jsonify({'success': True})
            
        except Exception as e:
            logger.error(f"Clear conversation error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

# Conversation export as specified in TDD
@api_bp.route('/export-conversation')
def export_conversation():
    """Export conversation as JSON as specified in TDD"""
    if not is_authenticated(session):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conversation = session.get('conversation', [])
        
        # Add export metadata
        export_data = {
            'exported_at': datetime.utcnow().isoformat(),
            'user': session.get('username'),
            'conversation_count': len(conversation),
            'conversation': conversation
        }
        
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = 'attachment; filename=conversation_export.json'
        
        logger.info(f"Conversation exported for user {session.get('username')}")
        return response
        
    except Exception as e:
        logger.error(f"Export conversation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Legacy endpoints for backward compatibility
@api_bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """Legacy synthesis endpoint (backward compatibility)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        character = data.get('character', os.getenv('AVATAR_CHARACTER', 'lisa'))
        style = data.get('style', os.getenv('AVATAR_STYLE', 'graceful-sitting'))
        voice = data.get('voice', os.getenv('TTS_VOICE', 'en-US-JennyNeural'))
        
        logger.info(f"Legacy synthesis request for text: {text[:50]}...")
        
        # Return simple success response
        return jsonify({
            'success': True,
            'message': 'Please use the new /api/chat endpoint',
            'character': character,
            'style': style,
            'voice': voice
        })
            
    except Exception as e:
        logger.error(f"Error in legacy synthesize_speech: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/avatars', methods=['GET'])
def get_available_avatars():
    """Legacy avatars endpoint (backward compatibility)"""
    try:
        avatars = avatar_manager.get_available_avatars()
        return jsonify({
            'success': True,
            'avatars': avatars
        })
    except Exception as e:
        logger.error(f"Error getting avatars: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/voices', methods=['GET'])
def get_available_voices():
    """Legacy voices endpoint (backward compatibility)"""
    try:
        if speech_service:
            voices = speech_service.get_available_voices()
        else:
            # Return default voices if service not available
            voices = avatar_manager.available_voices
            
        return jsonify({
            'success': True,
            'voices': voices
        })
    except Exception as e:
        logger.error(f"Error getting voices: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Legacy config endpoint (backward compatibility)"""
    try:
        config = avatar_manager.default_config
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/azure-config', methods=['GET'])
def azure_config():
    """
    Azure configuration endpoint for the Azure sample implementation.
    Returns necessary Azure service configuration for the frontend.
    """
    if not is_authenticated(session):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get Azure service configuration from environment
        config = {
            'speech_key': os.getenv('AZURE_SPEECH_KEY'),
            'speech_region': os.getenv('AZURE_SPEECH_REGION'),
            'openai_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
            'openai_key': os.getenv('AZURE_OPENAI_KEY'),
            'search_endpoint': os.getenv('AZURE_SEARCH_ENDPOINT'),
            'search_key': os.getenv('AZURE_SEARCH_KEY'),
            'search_index': os.getenv('AZURE_SEARCH_INDEX'),
            'avatar_character': os.getenv('AVATAR_CHARACTER', 'lisa'),
            'avatar_style': os.getenv('AVATAR_STYLE', 'casual-sitting')
        }
        
        # Filter out None values and only return configured services
        filtered_config = {k: v for k, v in config.items() if v is not None}
        
        return jsonify({
            'success': True,
            'config': filtered_config
        })
        
    except Exception as e:
        logger.error(f"Error getting azure config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
