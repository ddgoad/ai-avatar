"""
Input Processing Module

Unified input processing for voice and text exactly as specified in the Technical Design Document.
Handles both text input and Azure Speech-to-Text conversion for voice input.
"""

import logging
import os
import asyncio
from typing import Dict, Any, Optional
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)

class InputProcessor:
    """
    Unified input processing for voice and text inputs as specified in TDD.
    """
    
    def __init__(self, speech_service=None):
        """
        Initialize Input Processor with optional speech service.
        
        Args:
            speech_service: Azure Speech Service instance for voice processing
        """
        self.speech_service = speech_service
        logger.info("Input Processor initialized")
    
    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Convert voice to text using Azure Speech Services as specified in TDD.
        
        Args:
            audio_data: Raw audio data in WebM format
            
        Returns:
            Dictionary with processed input information
        """
        try:
            if not self.speech_service:
                raise ValueError("Speech service not configured")
            
            # Convert audio data using Azure Speech Service
            result = await self._transcribe_audio(audio_data)
            
            return {
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0.0),
                'input_type': 'voice',
                'success': result.get('success', False),
                'error': result.get('error')
            }
            
        except Exception as e:
            logger.error(f"Voice input processing error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'input_type': 'voice',
                'success': False,
                'error': str(e)
            }
    
    def process_text_input(self, text: str) -> Dict[str, Any]:
        """
        Process direct text input as specified in TDD.
        
        Args:
            text: Input text string
            
        Returns:
            Dictionary with processed input information
        """
        try:
            if not text or not text.strip():
                return {
                    'text': '',
                    'confidence': 0.0,
                    'input_type': 'text',
                    'success': False,
                    'error': 'Empty text input'
                }
            
            cleaned_text = text.strip()
            logger.info(f"Processed text input: {cleaned_text[:50]}...")
            
            return {
                'text': cleaned_text,
                'confidence': 1.0,  # Text input has full confidence
                'input_type': 'text',
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Text input processing error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'input_type': 'text',
                'success': False,
                'error': str(e)
            }
    
    async def process_input(self, input_data: Any, input_type: str) -> Dict[str, Any]:
        """
        Unified input processing as specified in TDD.
        
        Args:
            input_data: Input data (text string or audio bytes)
            input_type: Type of input ('text' or 'voice')
            
        Returns:
            Dictionary with processed input information
        """
        try:
            if input_type == 'voice':
                return await self.process_voice_input(input_data)
            elif input_type == 'text':
                return self.process_text_input(input_data)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
                
        except Exception as e:
            logger.error(f"Input processing error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'input_type': input_type,
                'success': False,
                'error': str(e)
            }
    
    async def _transcribe_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Transcribe audio data using Azure Speech Services.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Create speech config
            speech_key = os.getenv('AZURE_SPEECH_KEY')
            speech_region = os.getenv('AZURE_SPEECH_REGION')
            
            if not speech_key or not speech_region:
                raise ValueError("Azure Speech Service credentials not configured")
            
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region
            )
            
            # Configure for WebM audio format
            audio_format = speechsdk.audio.AudioStreamFormat(
                compressed_stream_format=speechsdk.audio.AudioStreamContainerFormat.OGG_OPUS
            )
            
            # Create audio stream from data
            audio_stream = speechsdk.audio.PushAudioInputStream(audio_format)
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
            
            # Create speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Write audio data to stream
            audio_stream.write(audio_data)
            audio_stream.close()
            
            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info(f"Speech recognized: {result.text}")
                return {
                    'text': result.text,
                    'confidence': 0.95,  # Azure Speech Service typically has high confidence
                    'success': True,
                    'error': None
                }
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized")
                return {
                    'text': '',
                    'confidence': 0.0,
                    'success': False,
                    'error': 'No speech recognized'
                }
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"Speech recognition canceled: {cancellation.reason}"
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - {cancellation.error_details}"
                logger.error(error_msg)
                return {
                    'text': '',
                    'confidence': 0.0,
                    'success': False,
                    'error': error_msg
                }
            else:
                error_msg = f"Unexpected speech recognition result: {result.reason}"
                logger.error(error_msg)
                return {
                    'text': '',
                    'confidence': 0.0,
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"Audio transcription error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        """
        Validate audio format for processing.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            True if format is valid, False otherwise
        """
        try:
            # Basic validation - check if data exists and has minimum size
            if not audio_data or len(audio_data) < 100:
                return False
            
            # Additional format validation could be added here
            return True
            
        except Exception as e:
            logger.error(f"Audio format validation error: {str(e)}")
            return False