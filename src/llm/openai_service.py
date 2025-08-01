"""
OpenAI Service Integration

Azure OpenAI integration with model selection exactly as specified in the Technical Design Document.
Supports GPT-4o and O3-mini models with conversation history management.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Azure OpenAI integration with model selection as specified in TDD.
    """
    
    def __init__(self):
        """
        Initialize Azure OpenAI service with configuration from environment.
        """
        try:
            # Azure OpenAI configuration
            self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            self.api_key = os.getenv("AZURE_OPENAI_KEY") 
            self.api_version = os.getenv("AZURE_OPENAI_API_VERSION",
                                         "2024-12-01-preview")
            
            if not self.azure_endpoint or not self.api_key:
                raise ValueError("Azure OpenAI credentials not configured")
            
            # Initialize client
            self.client = AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
            
            # Model deployments as specified in TDD
            self.models = {
                'gpt4o': os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT", "gpt-4o"),
                'o3-mini': os.getenv("AZURE_OPENAI_O3_MINI_DEPLOYMENT", 
                                   "o3-mini")
            }
            
            logger.info(f"OpenAI Service initialized with endpoint: {self.azure_endpoint}")
            logger.info(f"Available models: {list(self.models.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI Service: {str(e)}")
            raise
    
    def get_ai_response(
        self, 
        user_input: str, 
        model_choice: str = 'gpt4o', 
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate AI response with selected model as specified in TDD.
        
        Args:
            user_input: User's input text
            model_choice: Model to use ('gpt4o' or 'o3-mini')
            conversation_history: Previous conversation messages
            temperature: Randomness in response generation
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with AI response and metadata
        """
        try:
            # Validate model choice
            if model_choice not in self.models:
                logger.warning(f"Invalid model choice '{model_choice}', using default 'gpt4o'")
                model_choice = 'gpt4o'
            
            deployment = self.models[model_choice]
            
            # Build messages array
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                # Limit history to last 10 exchanges to stay within token limits
                recent_history = conversation_history[-20:]  # 10 user + 10 assistant messages
                messages.extend(recent_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            logger.info(f"Sending request to {deployment} with {len(messages)} messages")
            
            # Make API call
            response = self.client.chat.completions.create(
                model=deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            
            # Calculate token usage
            usage = response.usage
            tokens_used = usage.total_tokens if usage else 0
            
            logger.info(f"Received response from {model_choice}: {ai_response[:100]}...")
            logger.info(f"Tokens used: {tokens_used}")
            
            return {
                'content': ai_response,
                'model_used': model_choice,
                'deployment_used': deployment,
                'tokens_used': tokens_used,
                'prompt_tokens': usage.prompt_tokens if usage else 0,
                'completion_tokens': usage.completion_tokens if usage else 0,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"OpenAI API error: {str(e)}"
            logger.error(error_msg)
            return {
                'content': f"I'm sorry, I encountered an error processing your request: {str(e)}",
                'model_used': model_choice,
                'deployment_used': self.models.get(model_choice, 'unknown'),
                'tokens_used': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'success': False,
                'error': error_msg
            }
    
    def get_available_models(self) -> List[str]:
        """
        Return list of available models as specified in TDD.
        
        Returns:
            List of available model names
        """
        return list(self.models.keys())
    
    def get_model_info(self, model_choice: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_choice: Model name
            
        Returns:
            Dictionary with model information
        """
        if model_choice not in self.models:
            return {'error': f'Model {model_choice} not available'}
        
        model_info = {
            'gpt4o': {
                'name': 'GPT-4o',
                'description': 'Advanced multimodal model with superior reasoning',
                'max_tokens': 128000,
                'recommended_use': 'Complex conversations, reasoning, analysis'
            },
            'o3-mini': {
                'name': 'O3-mini', 
                'description': 'Efficient model for quick responses',
                'max_tokens': 128000,
                'recommended_use': 'Simple conversations, quick responses'
            }
        }
        
        return model_info.get(model_choice, {'error': 'Model info not available'})
    
    def format_conversation_history(self, conversation: List[Dict]) -> List[Dict]:
        """
        Format conversation history for API calls.
        
        Args:
            conversation: Raw conversation history
            
        Returns:
            Formatted messages for OpenAI API
        """
        formatted_messages = []
        
        for message in conversation:
            if message.get('role') in ['user', 'assistant']:
                formatted_messages.append({
                    'role': message['role'],
                    'content': message.get('content', '')
                })
        
        return formatted_messages
    
    def test_connection(self) -> bool:
        """
        Test connection to Azure OpenAI service.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test call
            response = self.get_ai_response(
                "Hello, this is a connection test.",
                model_choice='gpt4o',
                max_tokens=10
            )
            
            return response.get('success', False)
            
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False
    
    def count_tokens_estimate(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for English text
        return max(1, len(text) // 4)
    
    def truncate_conversation_history(
        self, 
        conversation: List[Dict], 
        max_tokens: int = 3000
    ) -> List[Dict]:
        """
        Truncate conversation history to fit within token limits.
        
        Args:
            conversation: Conversation history
            max_tokens: Maximum tokens to allow
            
        Returns:
            Truncated conversation history
        """
        if not conversation:
            return []
        
        # Start from the end and work backwards
        truncated = []
        total_tokens = 0
        
        for message in reversed(conversation):
            content = message.get('content', '')
            message_tokens = self.count_tokens_estimate(content)
            
            if total_tokens + message_tokens > max_tokens:
                break
                
            truncated.insert(0, message)
            total_tokens += message_tokens
        
        logger.info(f"Truncated conversation to {len(truncated)} messages (~{total_tokens} tokens)")
        return truncated