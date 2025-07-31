"""
Azure Speech Service Integration

Handles Azure AI Services Speech Service text-to-speech avatar functionality.
"""

import os
import logging
import azure.cognitiveservices.speech as speechsdk
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AzureSpeechService:
    """Azure Speech Service client for text-to-speech avatar functionality"""
    
    def __init__(self):
        """Initialize Azure Speech Service client"""
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.speech_region = os.getenv('AZURE_SPEECH_REGION')
        
        if not self.speech_key or not self.speech_region:
            raise ValueError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION must be set")
        
        # Create speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        
        logger.info(f"Initialized Azure Speech Service for region: {self.speech_region}")
    
    def synthesize_with_avatar(
        self, 
        text: str,
        character: str = "lisa",
        style: str = "graceful-sitting",
        voice: str = "en-US-JennyNeural",
        background_color: str = "#FFFFFFFF"
    ) -> Dict:
        """
        Synthesize speech with avatar using Azure Speech Service
        
        Args:
            text: Text to synthesize
            character: Avatar character (e.g., 'lisa', 'anna')
            style: Avatar style (e.g., 'graceful-sitting', 'standing')
            voice: TTS voice to use
            background_color: Background color in hex format
            
        Returns:
            Dict with success status and result data
        """
        try:
            # Set the voice
            self.speech_config.speech_synthesis_voice_name = voice
            
            # Create SSML with avatar configuration
            ssml = self._create_avatar_ssml(
                text=text,
                character=character,
                style=style,
                voice=voice,
                background_color=background_color
            )
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            
            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("Speech synthesis completed successfully")
                
                # Save audio to file (in a real implementation, you might save to blob storage)
                audio_filename = f"speech_{hash(text)}.wav"
                audio_path = os.path.join("static", "audio", audio_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                
                # Save audio data
                with open(audio_path, "wb") as audio_file:
                    audio_file.write(result.audio_data)
                
                return {
                    'success': True,
                    'audio_url': f"/static/audio/{audio_filename}",
                    'character': character,
                    'style': style,
                    'voice': voice
                }
            else:
                error_msg = f"Speech synthesis failed: {result.reason}"
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    error_msg += f" - {cancellation.reason}: {cancellation.error_details}"
                
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"Error in speech synthesis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_avatar_ssml(
        self,
        text: str,
        character: str,
        style: str,
        voice: str,
        background_color: str
    ) -> str:
        """
        Create SSML with avatar configuration
        
        Returns SSML string for text-to-speech avatar synthesis
        """
        rate = os.getenv('TTS_RATE', '0')
        pitch = os.getenv('TTS_PITCH', '0')
        
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                   xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice}">
                <mstts:ttsembedding speakerProfileId="{character}">
                    <mstts:express-as style="{style}">
                        <prosody rate="{rate}%" pitch="{pitch}%">
                            {text}
                        </prosody>
                    </mstts:express-as>
                </mstts:ttsembedding>
            </voice>
        </speak>'''
        
        return ssml
    
    def get_available_voices(self) -> List[Dict]:
        """
        Get list of available TTS voices
        
        Returns:
            List of voice information dictionaries
        """
        try:
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            voices = synthesizer.get_voices_async().get()
            
            voice_list = []
            for voice in voices.voices:
                voice_list.append({
                    'name': voice.name,
                    'display_name': voice.display_name,
                    'local_name': voice.local_name,
                    'locale': voice.locale,
                    'gender': voice.gender.name,
                    'voice_type': voice.voice_type.name
                })
            
            return voice_list
            
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test connection to Azure Speech Service
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple synthesis test
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            result = synthesizer.speak_text_async("Test").get()
            
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
