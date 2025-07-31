"""
Avatar Manager

Manages avatar characters, styles, and configurations for the AI Avatar service.
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AvatarManager:
    """Manages avatar characters, styles, and configurations"""
    
    def __init__(self):
        """Initialize Avatar Manager with default configurations"""
        self.available_characters = {
            'lisa': {
                'name': 'Lisa',
                'description': 'Professional female avatar',
                'styles': ['graceful-sitting', 'standing', 'casual-sitting']
            },
            'anna': {
                'name': 'Anna',
                'description': 'Friendly female avatar', 
                'styles': ['graceful-sitting', 'standing', 'friendly-sitting']
            },
            'mike': {
                'name': 'Mike',
                'description': 'Professional male avatar',
                'styles': ['graceful-sitting', 'standing', 'business-sitting']
            }
        }
        
        self.style_descriptions = {
            'graceful-sitting': 'Sitting gracefully in a professional manner',
            'standing': 'Standing upright in a professional pose',
            'casual-sitting': 'Sitting in a relaxed, casual manner',
            'friendly-sitting': 'Sitting in a warm, friendly manner',
            'business-sitting': 'Sitting in a formal business pose'
        }
        
        logger.info("Avatar Manager initialized")
    
    def get_available_avatars(self) -> Dict:
        """
        Get all available avatar characters and their styles
        
        Returns:
            Dictionary containing avatar characters and styles
        """
        return {
            'characters': self.available_characters,
            'styles': self.style_descriptions
        }
    
    def get_character_info(self, character: str) -> Dict:
        """
        Get information about a specific character
        
        Args:
            character: Character name
            
        Returns:
            Character information dictionary
        """
        if character in self.available_characters:
            return self.available_characters[character]
        else:
            logger.warning(f"Character '{character}' not found")
            return {}
    
    def validate_character_style(self, character: str, style: str) -> bool:
        """
        Validate if a style is available for a character
        
        Args:
            character: Character name
            style: Style name
            
        Returns:
            True if valid combination, False otherwise
        """
        if character not in self.available_characters:
            logger.warning(f"Character '{character}' not available")
            return False
        
        if style not in self.available_characters[character]['styles']:
            logger.warning(f"Style '{style}' not available for character '{character}'")
            return False
        
        return True
    
    def get_default_config(self) -> Dict:
        """
        Get default avatar configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            'character': os.getenv('AVATAR_CHARACTER', 'lisa'),
            'style': os.getenv('AVATAR_STYLE', 'graceful-sitting'),
            'background_color': os.getenv('AVATAR_BACKGROUND_COLOR', '#FFFFFFFF'),
            'voice': os.getenv('TTS_VOICE', 'en-US-JennyNeural'),
            'rate': int(os.getenv('TTS_RATE', 0)),
            'pitch': int(os.getenv('TTS_PITCH', 0))
        }
    
    def create_avatar_config(
        self, 
        character: Optional[str] = None,
        style: Optional[str] = None,
        background_color: Optional[str] = None,
        voice: Optional[str] = None,
        rate: Optional[int] = None,
        pitch: Optional[int] = None
    ) -> Dict:
        """
        Create avatar configuration with provided or default values
        
        Args:
            character: Avatar character
            style: Avatar style
            background_color: Background color
            voice: TTS voice
            rate: Speech rate adjustment
            pitch: Speech pitch adjustment
            
        Returns:
            Complete configuration dictionary
        """
        defaults = self.get_default_config()
        
        config = {
            'character': character or defaults['character'],
            'style': style or defaults['style'],
            'background_color': background_color or defaults['background_color'],
            'voice': voice or defaults['voice'],
            'rate': rate if rate is not None else defaults['rate'],
            'pitch': pitch if pitch is not None else defaults['pitch']
        }
        
        # Validate character and style combination
        if not self.validate_character_style(config['character'], config['style']):
            logger.warning("Invalid character/style combination, using defaults")
            config['character'] = defaults['character']
            config['style'] = defaults['style']
        
        return config
    
    def get_character_styles(self, character: str) -> List[str]:
        """
        Get available styles for a specific character
        
        Args:
            character: Character name
            
        Returns:
            List of available styles
        """
        if character in self.available_characters:
            return self.available_characters[character]['styles']
        else:
            logger.warning(f"Character '{character}' not found")
            return []
