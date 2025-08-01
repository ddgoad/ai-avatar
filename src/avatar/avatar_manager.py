"""
Avatar Manager - Real-Time WebRTC Implementation

Implementation based on Azure official samples for real-time avatar sessions.
Uses WebRTC for streaming video instead of file-based synthesis.
Reference: https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/samples/js/browser/avatar
"""

import os
import logging
import uuid
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)


class AvatarManager:
    """
    Real-time Avatar session manager based on Azure official samples.
    Manages WebRTC-based avatar sessions instead of file-based synthesis.
    """
    
    def __init__(self):
        """Initialize Avatar Manager for real-time sessions"""
        
        # Available characters as per Azure Speech SDK official documentation
        # Reference: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/avatar-gestures-with-ssml#supported-standard-avatar-characters-styles-and-gestures
        self.available_characters = [
            {'id': 'lisa', 'name': 'Lisa', 
             'description': 'Professional female avatar'},
            {'id': 'harry', 'name': 'Harry', 
             'description': 'Professional male avatar'},
            {'id': 'jeff', 'name': 'Jeff', 
             'description': 'Business male avatar'},
            {'id': 'lori', 'name': 'Lori', 
             'description': 'Friendly female avatar'},
            {'id': 'meg', 'name': 'Meg', 
             'description': 'Professional female avatar'},
            {'id': 'max', 'name': 'Max', 
             'description': 'Business male avatar'}
        ]
        
        # Available styles as per Azure Speech SDK official documentation
        # Note: For real-time synthesis, Lisa only supports 'casual-sitting'
        # All other Lisa styles are NOT supported for real-time API
        self.available_styles = [
            {'id': 'casual-sitting', 'name': 'Casual Sitting', 
             'description': 'Relaxed seated pose (Lisa only)'},
            {'id': 'business', 'name': 'Business', 
             'description': 'Professional business style'},
            {'id': 'casual', 'name': 'Casual', 
             'description': 'Relaxed casual style'},
            {'id': 'formal', 'name': 'Formal', 
             'description': 'Formal professional style'},
            {'id': 'youthful', 'name': 'Youthful', 
             'description': 'Young energetic style'}
        ]
        
        # Character/Style compatibility matrix for real-time synthesis
        # Based on Azure documentation - real-time API limitations
        self.character_style_matrix = {
            'lisa': ['casual-sitting'],  # Only casual-sitting for real-time
            'harry': ['business', 'casual', 'youthful'],
            'jeff': ['business', 'formal'],
            'lori': ['casual', 'formal'],  # graceful not in real-time
            'meg': ['formal', 'casual', 'business'],
            'max': ['business', 'casual', 'formal']
        }
        
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
            'style': 'casual-sitting',  # Only style supported for Lisa in real-time
            'voice': 'en-US-JennyNeural',
            'background': 'solid-white',
            'gesture': None,
            'video_quality': 'high'
        }
        
        # Active avatar sessions (session_id -> session_info)
        self.active_sessions = {}
        
        logger.info("Real-time Avatar Manager initialized (WebRTC-based)")
    
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
        
        # Update with user preferences
        for key, value in user_preferences.items():
            if key in config:
                config[key] = value
        
        # Build background configuration
        background_id = config.get('background', 'solid-white')
        background_info = next(
            (bg for bg in self.background_options if bg['id'] == background_id),
            self.background_options[0]
        )
        
        config['background_config'] = {
            'type': background_info['type'],
            'value': background_info['value']
        }
        
        # Add video format settings
        quality = config.get('video_quality', 'high')
        if quality == 'high':
            config['video_format'] = {
                'resolution': '1080p',
                'bitrate': 2000000,
                'codec': 'h264'
            }
        else:
            config['video_format'] = {
                'resolution': '720p',
                'bitrate': 1000000,
                'codec': 'h264'
            }
        
        return config
    
    async def get_ice_token(self) -> Dict[str, Any]:
        """
        Get ICE server token for WebRTC connection (based on Azure samples).
        
        Returns:
            ICE token information
        """
        try:
            # Get Azure Speech credentials
            speech_key = os.getenv('AZURE_SPEECH_KEY')
            speech_region = os.getenv('AZURE_SPEECH_REGION')
            
            if not speech_key or not speech_region:
                raise ValueError("Azure Speech credentials not configured")
            
            # ICE token endpoint (based on official samples)
            ice_token_url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/avatar/relay/token/v1"
            
            headers = {
                'Ocp-Apim-Subscription-Key': speech_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(ice_token_url, headers=headers) as response:
                    if response.status == 200:
                        ice_token_data = await response.json()
                        logger.info("ICE token retrieved successfully")
                        return {
                            'success': True,
                            'ice_servers': [{
                                'urls': ice_token_data['Urls'],
                                'username': ice_token_data['Username'],
                                'credential': ice_token_data['Password']
                            }],
                            'error': None
                        }
                    else:
                        error_msg = f"Failed to get ICE token: {response.status}"
                        logger.error(error_msg)
                        return {
                            'success': False,
                            'ice_servers': None,
                            'error': error_msg
                        }
                        
        except Exception as e:
            logger.error(f"ICE token retrieval error: {str(e)}")
            return {
                'success': False,
                'ice_servers': None,
                'error': str(e)
            }
    
    async def create_avatar_session(self, client_id: str, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and configure avatar session (based on Azure samples).
        This sets up the server-side avatar session that will connect to the WebRTC frontend.
        
        Args:
            client_id: Unique client identifier
            avatar_config: Avatar configuration
            
        Returns:
            Session creation result
        """
        try:
            # Get Azure Speech credentials
            speech_key = os.getenv('AZURE_SPEECH_KEY')
            speech_region = os.getenv('AZURE_SPEECH_REGION')
            
            if not speech_key or not speech_region:
                raise ValueError("Azure Speech credentials not configured")
            
            # Create session ID
            session_id = str(uuid.uuid4())
            
            # Configure speech synthesizer for avatar (based on official samples)
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region
            )
            
            # Set voice name
            voice_name = avatar_config.get('voice', 'en-US-JennyNeural')
            speech_config.speech_synthesis_voice_name = voice_name
            
            # Configure for avatar synthesis
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_SynthEnableCompressedAudioTransmission,
                "false"
            )
            
            # Store session information
            session_info = {
                'session_id': session_id,
                'client_id': client_id,
                'avatar_config': avatar_config,
                'speech_config': speech_config,
                'created_at': asyncio.get_event_loop().time(),
                'active': True
            }
            
            self.active_sessions[session_id] = session_info
            
            logger.info(f"Avatar session created: {session_id} for client: {client_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Avatar session creation error: {str(e)}")
            return {
                'success': False,
                'session_id': None,
                'error': str(e)
            }
    
    async def synthesize_speech_to_avatar(self, session_id: str, text: str) -> Dict[str, Any]:
        """
        Send text to avatar session for real-time speech synthesis (based on Azure samples).
        This sends text to an active avatar session for immediate synthesis and streaming.
        
        Args:
            session_id: Session identifier
            text: Text to synthesize
            
        Returns:
            Synthesis result
        """
        try:
            # Check if session exists
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_info = self.active_sessions[session_id]
            if not session_info['active']:
                raise ValueError(f"Session {session_id} is not active")
            
            # Get speech configuration
            speech_config = session_info['speech_config']
            avatar_config = session_info['avatar_config']
            
            # Add gesture to text if specified
            gesture = avatar_config.get('gesture')
            if gesture:
                # Create SSML with gesture
                voice_name = avatar_config.get('voice', 'en-US-JennyNeural')
                ssml_text = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
                    <voice name="{voice_name}">
                        <mstts:viseme type="{gesture}"/>
                        {text}
                    </voice>
                </speak>
                """
            else:
                # Simple SSML
                voice_name = avatar_config.get('voice', 'en-US-JennyNeural')
                ssml_text = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                    <voice name="{voice_name}">{text}</voice>
                </speak>
                """
            
            # Create speech synthesizer for this session
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            
            # Perform synthesis (this will stream to the WebRTC session)
            logger.info(f"Synthesizing text for session {session_id}: {text[:50]}...")
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: synthesizer.speak_ssml_async(ssml_text).get()
            )
            
            # Check synthesis result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Speech synthesis completed for session {session_id}")
                return {
                    'success': True,
                    'duration': result.audio_duration.total_seconds() if hasattr(result, 'audio_duration') else 0,
                    'error': None
                }
            else:
                error_msg = f"Speech synthesis failed: {result.reason}"
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    error_msg += f" - {cancellation.reason}: {cancellation.error_details}"
                
                logger.error(error_msg)
                return {
                    'success': False,
                    'duration': 0,
                    'error': error_msg
                }
            
        except Exception as e:
            logger.error(f"Avatar speech synthesis error: {str(e)}")
            return {
                'success': False,
                'duration': 0,
                'error': str(e)
            }
    
    async def close_avatar_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close avatar session and clean up resources.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Close result
        """
        try:
            if session_id in self.active_sessions:
                session_info = self.active_sessions[session_id]
                session_info['active'] = False
                
                # Clean up session
                del self.active_sessions[session_id]
                
                logger.info(f"Avatar session closed: {session_id}")
                return {
                    'success': True,
                    'error': None
                }
            else:
                logger.warning(f"Session {session_id} not found for closing")
                return {
                    'success': False,
                    'error': 'Session not found'
                }
                
        except Exception as e:
            logger.error(f"Error closing avatar session: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs.
        
        Returns:
            List of active session IDs
        """
        return [
            session_id for session_id, info in self.active_sessions.items()
            if info['active']
        ]
    
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
        ONLY uses the real Azure Avatar API - no fallbacks.
        
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
            
            if not AVATAR_SDK_AVAILABLE:
                raise ImportError("Azure Avatar SDK is required but not available")
            
            # Create speech config
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region
            )
            
            # Configure avatar synthesis
            logger.info(f"Synthesizing LIVE avatar video with config: {avatar_config}")
            logger.info(f"SSML: {ssml_text[:200]}...")
            
            # Configure avatar video format from user preferences
            video_format = avatar_config.get('video_format', {})
            codec = video_format.get('codec', 'h264')
            bitrate = video_format.get('bitrate', 2000000)
            resolution = video_format.get('resolution', '1080p')
            
            # Set video format for avatar synthesis
            speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_SynthVideoFormat, "webm")
            
            # Create avatar configuration from user settings
            avatar_character = avatar_config.get('character', 'lisa')
            avatar_style = avatar_config.get('style', 'graceful-sitting')
            background = avatar_config.get('background', {})
            voice_name = avatar_config.get('voice', 'en-US-JennyNeural')
            
            # Set background configuration
            if background.get('type') == 'color':
                background_color = background.get('value', '#FFFFFF')
            elif background.get('type') == 'transparent':
                background_color = 'transparent'
            else:
                background_color = '#FFFFFF'  # Default
            
            # Use real Azure Avatar API
            logger.info("Using Azure Text-to-Speech Avatar API for LIVE video generation")
            
            # Configure avatar synthesis using speech config properties
            # Set the avatar character and style
            speech_config.set_property("AZURE_SPEECH_AVATAR_CHARACTER", avatar_character)
            speech_config.set_property("AZURE_SPEECH_AVATAR_STYLE", avatar_style)
            speech_config.set_property("AZURE_SPEECH_AVATAR_BACKGROUND_COLOR", background_color)
            
            # Configure video format for avatar synthesis
            speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_SynthVideoFormat, "mp4")
            speech_config.set_property("AZURE_SPEECH_AVATAR_VIDEO_BITRATE", str(bitrate))
            
            # Set voice for synthesis
            speech_config.speech_synthesis_voice_name = voice_name
            
            # Create synthesizer for avatar video
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            
            # Perform avatar video synthesis
            logger.info(f"Starting LIVE avatar synthesis with character: {avatar_character}, style: {avatar_style}, voice: {voice_name}")
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: synthesizer.speak_ssml_async(ssml_text).get()
            )
            
            # Check if synthesis was successful
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("LIVE Avatar video synthesis completed successfully")
                
                # Get video data from result
                video_data = result.video_data if hasattr(result, 'video_data') else None
                
                if video_data and len(video_data) > 0:
                    logger.info(f"LIVE Avatar video generated: {len(video_data)} bytes")
                    return {
                        'success': True,
                        'video_data': video_data,
                        'duration': result.audio_duration.total_seconds() if hasattr(result, 'audio_duration') else 0,
                        'error': None
                    }
                else:
                    raise Exception("Avatar API returned no video data")
            else:
                error_msg = f"Avatar synthesis failed: {result.reason}"
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    error_msg += f" - {cancellation.reason}: {cancellation.error_details}"
                
                logger.error(error_msg)
                raise Exception(error_msg)
            
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
        Store video in Azure Blob Storage and return ID.
        
        Args:
            video_data: Video data to store
            
        Returns:
            Unique video ID
        """
        try:
            video_id = str(uuid.uuid4())
            
            # Get Azure Storage connection string
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("Azure Storage not configured - required for Avatar API")
            
            # Create blob service client
            blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
            
            # Container name for avatar videos
            container_name = "avatars"
            
            # Create container if it doesn't exist
            try:
                blob_service_client.create_container(container_name)
            except Exception:
                pass  # Container might already exist
            
            # Upload video to blob storage
            blob_name = f"{video_id}.mp4"
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(video_data, overwrite=True)
            
            logger.info(
                f"LIVE Avatar video stored in Azure Blob Storage with ID: {video_id}"
            )
            return video_id
            
        except Exception as e:
            logger.error(f"Azure Blob Storage error: {str(e)}")
            raise Exception(f"Failed to store avatar video: {str(e)}")
    
    def get_video_path(self, video_id: str) -> Optional[str]:
        """
        Get URL to stored video with SAS token for authenticated access.
        
        Args:
            video_id: Video ID
            
        Returns:
            URL to video file with SAS token
        """
        try:
            # Check if using Azure Blob Storage
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("Azure Storage not configured")
            
            # Return blob URL with SAS token for Azure storage
            blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
            container_name = "avatars"
            blob_name = f"{video_id}.mp4"
            
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Check if blob exists
            try:
                blob_client.get_blob_properties()
                
                # Generate SAS token for blob access (valid for 1 hour)
                from azure.storage.blob import (
                    generate_blob_sas, BlobSasPermissions
                )
                from datetime import datetime, timedelta
                
                # Get account name and key from connection string
                account_name = blob_service_client.account_name
                account_key = blob_service_client.credential.account_key
                
                sas_token = generate_blob_sas(
                    account_name=account_name,
                    container_name=container_name,
                    blob_name=blob_name,
                    account_key=account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=1)
                )
                
                # Return URL with SAS token
                return f"{blob_client.url}?{sas_token}"
                
            except Exception as e:
                logger.warning(
                    f"LIVE Avatar video {video_id} not found in Azure storage: "
                    f"{str(e)}"
                )
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
