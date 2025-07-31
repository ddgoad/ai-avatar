"""
AI Avatar API Routes

Flask blueprint containing API endpoints for avatar functionality.
"""

import os
import logging
from flask import Blueprint, request, jsonify
from src.speech.azure_speech import AzureSpeechService
from src.avatar.avatar_manager import AvatarManager

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
speech_service = AzureSpeechService()
avatar_manager = AvatarManager()

@api_bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """
    Synthesize speech with avatar
    
    Expected JSON payload:
    {
        "text": "Hello, world!",
        "character": "lisa",
        "style": "graceful-sitting",
        "voice": "en-US-JennyNeural"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        character = data.get('character', os.getenv('AVATAR_CHARACTER', 'lisa'))
        style = data.get('style', os.getenv('AVATAR_STYLE', 'graceful-sitting'))
        voice = data.get('voice', os.getenv('TTS_VOICE', 'en-US-JennyNeural'))
        
        logger.info(f"Synthesizing speech for text: {text[:50]}...")
        
        # Generate speech with avatar
        result = speech_service.synthesize_with_avatar(
            text=text,
            character=character,
            style=style,
            voice=voice
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'audio_url': result['audio_url'],
                'video_url': result.get('video_url'),
                'character': character,
                'style': style,
                'voice': voice
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Error in synthesize_speech: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/avatars', methods=['GET'])
def get_available_avatars():
    """Get list of available avatar characters and styles"""
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
    """Get list of available TTS voices"""
    try:
        voices = speech_service.get_available_voices()
        return jsonify({
            'success': True,
            'voices': voices
        })
    except Exception as e:
        logger.error(f"Error getting voices: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Get current avatar configuration"""
    try:
        config = {
            'character': os.getenv('AVATAR_CHARACTER', 'lisa'),
            'style': os.getenv('AVATAR_STYLE', 'graceful-sitting'),
            'voice': os.getenv('TTS_VOICE', 'en-US-JennyNeural'),
            'background_color': os.getenv('AVATAR_BACKGROUND_COLOR', '#FFFFFFFF'),
            'rate': int(os.getenv('TTS_RATE', 0)),
            'pitch': int(os.getenv('TTS_PITCH', 0))
        }
        
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
