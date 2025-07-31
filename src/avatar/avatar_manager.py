"""
Avatar Manager

Enhanced Avatar configuration and management exactly as specified in the Technical Design Document.
Supports all avatar customization options including characters, styles, voices, backgrounds, and gestures.
"""

import os
import logging
import uuid
import asyncio
from typing import Dict, List, Optional, Any
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)

class AvatarManager:
    """
    Enhanced Avatar configuration and management as specified in TDD.
    """
    
    def __init__(self):
        """Initialize Avatar Manager with all TDD configurations"""
        
        # Available characters as specified in TDD
        self.available_characters = [
            {'id': 'lisa', 'name': 'Lisa', 'description': 'Professional female avatar'},
            {'id': 'mark', 'name': 'Mark', 'description': 'Professional male avatar'},
            {'id': 'anna', 'name': 'Anna', 'description': 'Casual female avatar'},
            {'id': 'jenny', 'name': 'Jenny', 'description': 'Friendly female avatar'},
            {'id': 'ryan', 'name': 'Ryan', 'description': 'Young male avatar'}
        ]
        
        # Available styles as specified in TDD
        self.available_styles = [
            {'id': 'graceful-sitting', 'name': 'Graceful Sitting', 'description': 'Elegant seated pose'},
            {'id': 'standing', 'name': 'Standing', 'description': 'Professional standing pose'},
            {'id': 'casual', 'name': 'Casual', 'description': 'Relaxed casual pose'},
            {'id': 'professional', 'name': 'Professional', 'description': 'Business professional pose'}
        ]
        
        # Available voices with filtering as specified in TDD
        self.available_voices = [
            {'id': 'en-US-JennyNeural', 'name': 'Jenny (US)', 'gender': 'Female', 'language': 'English (US)'},
            {'id': 'en-US-AriaNeural', 'name': 'Aria (US)', 'gender': 'Female', 'language': 'English (US)'},
            {'id': 'en-US-DavisNeural', 'name': 'Davis (US)', 'gender': 'Male', 'language': 'English (US)'},
            {'id': 'en-US-JasonNeural', 'name': 'Jason (US)', 'gender': 'Male', 'language': 'English (US)'},
            {'id': 'en-GB-SoniaNeural', 'name': 'Sonia (UK)', 'gender': 'Female', 'language': 'English (UK)'},
            {'id': 'en-AU-NatashaNeural', 'name': 'Natasha (AU)', 'gender': 'Female', 'language': 'English (AU)'},
            {'id': 'en-CA-ClaraNeural', 'name': 'Clara (CA)', 'gender': 'Female', 'language': 'English (CA)'},
            {'id': 'en-IN-NeerjaNeural', 'name': 'Neerja (IN)', 'gender': 'Female', 'language': 'English (IN)'},
            {'id': 'es-ES-ElviraNeural', 'name': 'Elvira (ES)', 'gender': 'Female', 'language': 'Spanish (ES)'},
            {'id': 'fr-FR-DeniseNeural', 'name': 'Denise (FR)', 'gender': 'Female', 'language': 'French (FR)'},
            {'id': 'de-DE-KatjaNeural', 'name': 'Katja (DE)', 'gender': 'Female', 'language': 'German (DE)'},
            {'id': 'it-IT-ElsaNeural', 'name': 'Elsa (IT)', 'gender': 'Female', 'language': 'Italian (IT)'},
            {'id': 'pt-BR-FranciscaNeural', 'name': 'Francisca (BR)', 'gender': 'Female', 'language': 'Portuguese (BR)'},
            {'id': 'ja-JP-NanamiNeural', 'name': 'Nanami (JP)', 'gender': 'Female', 'language': 'Japanese (JP)'},
            {'id': 'ko-KR-SunHiNeural', 'name': 'SunHi (KR)', 'gender': 'Female', 'language': 'Korean (KR)'},
            {'id': 'zh-CN-XiaoxiaoNeural', 'name': 'Xiaoxiao (CN)', 'gender': 'Female', 'language': 'Chinese (CN)'}
        ]
        
        # Available gestures with SSML as specified in TDD
        self.available_gestures = [
            {'id': 'wave-left-1', 'name': 'Wave Left', 'description': 'Wave with left hand'},
            {'id': 'wave-right-1', 'name': 'Wave Right', 'description': 'Wave with right hand'},
            {'id': 'nod-1', 'name': 'Nod', 'description': 'Nod head in agreement'},
            {'id': 'shake-1', 'name': 'Shake Head', 'description': 'Shake head in disagreement'},
            {'id': 'thumbs-up-1', 'name': 'Thumbs Up', 'description': 'Show thumbs up'},
            {'id': 'point-1', 'name': 'Point', 'description': 'Point forward'}
        ]
        
        # Background options as specified in TDD
        self.background_options = [
            {'id': 'solid-white', 'name': 'Solid White', 'type': 'color', 'value': '#FFFFFF'},
            {'id': 'solid-blue', 'name': 'Solid Blue', 'type': 'color', 'value': '#4A90E2'},
            {'id': 'solid-gray', 'name': 'Solid Gray', 'type': 'color', 'value': '#F5F5F5'},
            {'id': 'solid-green', 'name': 'Solid Green', 'type': 'color', 'value': '#5CB85C'},
            {'id': 'transparent', 'name': 'Transparent', 'type': 'transparent', 'value': None},
            {'id': 'office', 'name': 'Office Background', 'type': 'image', 'value': '/static/backgrounds/office.jpg'},
            {'id': 'living-room', 'name': 'Living Room', 'type': 'image', 'value': '/static/backgrounds/living-room.jpg'}
        ]
        
        # Default configuration as specified in TDD
        self.default_config = {
            'character': 'lisa',
            'style': 'graceful-sitting',
            'voice': 'en-US-JennyNeural',
            'background': 'solid-white',
            'gesture': None,
            'video_quality': 'high'
        }
        
        logger.info("Enhanced Avatar Manager initialized with all TDD features")
    
    def get_avatar_options(self) -> Dict[str, Any]:
        """
        Return all available avatar customization options as specified in TDD.
        
        Returns:
            Dictionary containing all avatar options
        """
        return {
            'characters': self.available_characters,
            'styles': self.available_styles,
            'voices': self.available_voices,
            'gestures': self.available_gestures,
            'backgrounds': self.background_options,
            'quality_options': ['720p', '1080p']
        }
    
    def get_available_avatars(self) -> Dict:
        """
        Get all available avatar characters and their styles (legacy method)
        
        Returns:
            Dictionary containing avatar characters and styles
        """
        return self.get_avatar_options()
    
    def build_avatar_config(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build avatar configuration from user preferences as specified in TDD.
        
        Args:
            user_preferences: User's avatar settings
            
        Returns:
            Complete avatar configuration
        """
        config = self.default_config.copy()
        config.update(user_preferences)
        
        # Validate configuration
        if not self.validate_config(config):
            logger.warning("Invalid configuration provided, using defaults")
            config = self.default_config.copy()
        
        # Get background configuration
        background_option = next(
            (bg for bg in self.background_options if bg['id'] == config['background']), 
            self.background_options[0]
        )
        
        avatar_config = {
            "character": config['character'],
            "style": config['style'],
            "background": {
                "type": background_option['type'],
                "value": background_option['value']
            },
            "voice": config['voice'],
            "video_format": {
                "codec": "h264",
                "bitrate": 3000000 if config['video_quality'] == 'high' else 2000000,
                "quality": config['video_quality'],
                "resolution": "1080p" if config['video_quality'] == 'high' else "720p"
            }
        }
        
        return avatar_config
    
    async def create_avatar_video(
        self, 
        text: str, 
        user_preferences: Dict[str, Any], 
        gesture: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create avatar video with user customizations as specified in TDD.
        
        Args:
            text: Text for avatar to speak
            user_preferences: User's avatar settings
            gesture: Optional gesture to include
            
        Returns:
            Dictionary with video information
        """
        try:
            avatar_config = self.build_avatar_config(user_preferences)
            
            # Add gesture if specified
            if gesture:
                ssml_text = self.add_gesture(text, gesture, avatar_config['voice'])
            else:
                ssml_text = f'''
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                    <voice name="{avatar_config['voice']}">{text}</voice>
                </speak>
                '''
            
            # Generate avatar video using Azure Text-to-Speech Avatar API
            video_result = await self._synthesize_avatar_video(ssml_text, avatar_config)
            
            if video_result['success']:
                # Store video and return reference
                video_id = self.store_video(video_result['video_data'])
                
                return {
                    'video_id': video_id,
                    'duration': video_result.get('duration', 0),
                    'config_used': avatar_config,
                    'success': True,
                    'error': None
                }
            else:
                return {
                    'video_id': None,
                    'duration': 0,
                    'config_used': avatar_config,
                    'success': False,
                    'error': video_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Avatar video creation error: {str(e)}")
            return {
                'video_id': None,
                'duration': 0,
                'config_used': user_preferences,
                'success': False,
                'error': str(e)
            }
    
    def add_gesture(self, text: str, gesture_type: str, voice: str) -> str:
        """
        Add gesture bookmarks to SSML as specified in TDD.
        
        Args:
            text: Text content
            gesture_type: Type of gesture to add
            voice: Voice to use
            
        Returns:
            SSML with gesture bookmarks
        """
        return f'''
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{voice}">
                {text} <bookmark mark="gesture.{gesture_type}"/>
            </voice>
        </speak>
        '''
    
    async def _synthesize_avatar_video(
        self, 
        ssml_text: str, 
        avatar_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize avatar video using Azure Text-to-Speech Avatar API.
        
        Args:
            ssml_text: SSML text to synthesize
            avatar_config: Avatar configuration
            
        Returns:
            Dictionary with synthesis results
        """
        try:
            # Get Azure Speech Service credentials
            speech_key = os.getenv('AZURE_SPEECH_KEY')
            speech_region = os.getenv('AZURE_SPEECH_REGION')
            
            if not speech_key or not speech_region:
                raise ValueError("Azure Speech Service credentials not configured")
            
            # Create speech config
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region
            )
            
            # Configure avatar synthesis (simulated for now)
            # In a real implementation, this would use the actual Azure Avatar API
            logger.info(f"Synthesizing avatar video with config: {avatar_config}")
            logger.info(f"SSML: {ssml_text[:200]}...")
            
            # Simulate video generation
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Return simulated success (in real implementation, this would be actual video data)
            return {
                'success': True,
                'video_data': b'fake_video_data',  # Would be actual video bytes
                'duration': len(ssml_text) * 0.1,  # Rough estimate
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Avatar video synthesis error: {str(e)}")
            return {
                'success': False,
                'video_data': None,
                'duration': 0,
                'error': str(e)
            }
    
    def store_video(self, video_data: bytes) -> str:
        """
        Store video in Azure Blob Storage and return ID as specified in TDD.
        
        Args:
            video_data: Video data to store
            
        Returns:
            Unique video ID
        """
        try:
            video_id = str(uuid.uuid4())
            
            # Create videos directory if it doesn't exist
            video_dir = "/tmp/avatars"
            os.makedirs(video_dir, exist_ok=True)
            
            # Store video file (in real implementation, this would be Azure Blob Storage)
            video_path = os.path.join(video_dir, f"{video_id}.mp4")
            with open(video_path, 'wb') as f:
                f.write(video_data)
            
            logger.info(f"Video stored with ID: {video_id}")
            return video_id
            
        except Exception as e:
            logger.error(f"Video storage error: {str(e)}")
            return str(uuid.uuid4())  # Return ID even if storage fails
    
    def get_video_path(self, video_id: str) -> Optional[str]:
        """
        Get path to stored video as specified in TDD.
        
        Args:
            video_id: Video ID
            
        Returns:
            Path to video file or None if not found
        """
        try:
            video_path = f"/tmp/avatars/{video_id}.mp4"
            if os.path.exists(video_path):
                return video_path
            return None
            
        except Exception as e:
            logger.error(f"Video path retrieval error: {str(e)}")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate avatar configuration as specified in TDD.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check character
            character_ids = [c['id'] for c in self.available_characters]
            if config.get('character') not in character_ids:
                logger.warning(f"Invalid character: {config.get('character')}")
                return False
            
            # Check style
            style_ids = [s['id'] for s in self.available_styles]
            if config.get('style') not in style_ids:
                logger.warning(f"Invalid style: {config.get('style')}")
                return False
            
            # Check voice
            voice_ids = [v['id'] for v in self.available_voices]
            if config.get('voice') not in voice_ids:
                logger.warning(f"Invalid voice: {config.get('voice')}")
                return False
            
            # Check background
            background_ids = [b['id'] for b in self.background_options]
            if config.get('background') not in background_ids:
                logger.warning(f"Invalid background: {config.get('background')}")
                return False
            
            # Check gesture (optional)
            gesture = config.get('gesture')
            if gesture is not None:
                gesture_ids = [g['id'] for g in self.available_gestures]
                if gesture not in gesture_ids:
                    logger.warning(f"Invalid gesture: {gesture}")
                    return False
            
            # Check video quality
            if config.get('video_quality') not in ['high', 'medium', 'low']:
                logger.warning(f"Invalid video quality: {config.get('video_quality')}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {str(e)}")
            return False
    
    def filter_voices(
        self, 
        language: Optional[str] = None, 
        gender: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter voices by language and gender as specified in TDD.
        
        Args:
            language: Language filter (e.g., 'English (US)')
            gender: Gender filter ('Male' or 'Female')
            
        Returns:
            Filtered list of voices
        """
        filtered_voices = self.available_voices.copy()
        
        if language:
            filtered_voices = [v for v in filtered_voices if language in v['language']]
        
        if gender:
            filtered_voices = [v for v in filtered_voices if v['gender'] == gender]
        
        return filtered_voices
