"""
Chat Functionality Tests for AI Avatar Application

Tests the core chat functionality including text/voice input processing,
AI response generation, and avatar video playback as specified in TDD.
"""

import pytest
from playwright.async_api import expect
import asyncio

class TestChatFunctionality:
    """Test chat functionality and message processing."""
    
    @pytest.mark.asyncio
    async def test_send_text_message(self, authenticated_page, test_messages):
        """Test sending a text message and receiving response."""
        # Type message in text input
        await authenticated_page.fill("#text-input", test_messages["short_message"])
        
        # Send message
        await authenticated_page.click("#send-button")
        
        # Check that message appears in chat
        await expect(authenticated_page.locator(".user-message")).to_be_visible()
        await expect(authenticated_page.locator(".user-message")).to_contain_text(test_messages["short_message"])
        
        # Wait for AI response (with timeout)
        await expect(authenticated_page.locator(".assistant-message")).to_be_visible(timeout=10000)
    
    @pytest.mark.asyncio
    async def test_send_message_with_enter_key(self, authenticated_page, test_messages):
        """Test sending message with Enter key."""
        # Type message
        await authenticated_page.fill("#text-input", test_messages["short_message"])
        
        # Press Enter to send
        await authenticated_page.keyboard.press("Enter")
        
        # Check message was sent
        await expect(authenticated_page.locator(".user-message")).to_be_visible()
        await expect(authenticated_page.locator(".user-message")).to_contain_text(test_messages["short_message"])
    
    @pytest.mark.asyncio
    async def test_shift_enter_new_line(self, authenticated_page):
        """Test that Shift+Enter creates new line instead of sending."""
        # Type message
        await authenticated_page.fill("#text-input", "Line 1")
        
        # Press Shift+Enter for new line
        await authenticated_page.keyboard.press("Shift+Enter")
        await authenticated_page.type("#text-input", "Line 2")
        
        # Should not have sent message yet
        message_count = await authenticated_page.locator(".user-message").count()
        assert message_count == 0
        
        # Text should contain both lines
        text_value = await authenticated_page.locator("#text-input").input_value()
        assert "Line 1" in text_value and "Line 2" in text_value
    
    @pytest.mark.asyncio
    async def test_empty_message_handling(self, authenticated_page):
        """Test that empty messages are not sent."""
        # Try to send empty message
        await authenticated_page.click("#send-button")
        
        # No message should appear in chat
        message_count = await authenticated_page.locator(".user-message").count()
        assert message_count == 0
        
        # Try with whitespace only
        await authenticated_page.fill("#text-input", "   ")
        await authenticated_page.click("#send-button")
        
        # Still no message should appear
        message_count = await authenticated_page.locator(".user-message").count()
        assert message_count == 0
    
    @pytest.mark.asyncio
    async def test_long_message_handling(self, authenticated_page, test_messages):
        """Test handling of long text messages."""
        # Send long message
        await authenticated_page.fill("#text-input", test_messages["long_message"])
        await authenticated_page.click("#send-button")
        
        # Check message appears correctly
        await expect(authenticated_page.locator(".user-message")).to_be_visible()
        await expect(authenticated_page.locator(".user-message")).to_contain_text(test_messages["long_message"][:50])
    
    @pytest.mark.asyncio
    async def test_special_characters_handling(self, authenticated_page, test_messages):
        """Test handling of special characters in messages."""
        # Send message with special characters
        await authenticated_page.fill("#text-input", test_messages["special_chars"])
        await authenticated_page.click("#send-button")
        
        # Check message appears correctly
        await expect(authenticated_page.locator(".user-message")).to_be_visible()
        await expect(authenticated_page.locator(".user-message")).to_contain_text("@#$%^&*()")
    
    @pytest.mark.asyncio
    async def test_message_timestamp_display(self, authenticated_page, test_messages):
        """Test that messages show timestamps."""
        # Send message
        await authenticated_page.fill("#text-input", test_messages["short_message"])
        await authenticated_page.click("#send-button")
        
        # Check timestamp is displayed
        await expect(authenticated_page.locator(".user-message .timestamp")).to_be_visible()
        
        # Timestamp should contain time format
        timestamp_text = await authenticated_page.locator(".user-message .timestamp").text_content()
        assert ":" in timestamp_text  # Should contain time format like "12:34"
    
    @pytest.mark.asyncio
    async def test_message_type_indicators(self, authenticated_page, test_messages):
        """Test that messages show type indicators (text/voice)."""
        # Send text message
        await authenticated_page.fill("#text-input", test_messages["short_message"])
        await authenticated_page.click("#send-button")
        
        # Check for text indicator
        await expect(authenticated_page.locator(".user-message .type-icon")).to_be_visible()
        type_icon = await authenticated_page.locator(".user-message .type-icon").text_content()
        assert "💬" in type_icon
    
    @pytest.mark.asyncio
    async def test_conversation_history_persistence(self, authenticated_page, test_messages):
        """Test that conversation history persists during session."""
        # Send first message
        await authenticated_page.fill("#text-input", "First message")
        await authenticated_page.click("#send-button")
        
        # Send second message
        await authenticated_page.fill("#text-input", "Second message")
        await authenticated_page.click("#send-button")
        
        # Check both messages are visible
        messages = await authenticated_page.locator(".user-message").count()
        assert messages == 2
        
        # Check messages are in correct order
        first_message = authenticated_page.locator(".user-message").first
        await expect(first_message).to_contain_text("First message")
    
    @pytest.mark.asyncio
    async def test_clear_conversation(self, authenticated_page, test_messages):
        """Test clearing conversation history."""
        # Send a message first
        await authenticated_page.fill("#text-input", test_messages["short_message"])
        await authenticated_page.click("#send-button")
        
        # Verify message exists
        await expect(authenticated_page.locator(".user-message")).to_be_visible()
        
        # Clear conversation
        await authenticated_page.click("#clear-conversation")
        
        # Check messages are cleared
        message_count = await authenticated_page.locator(".message").count()
        assert message_count == 0
    
    @pytest.mark.asyncio
    async def test_loading_indicator_during_processing(self, authenticated_page, test_messages):
        """Test that loading indicator shows during message processing."""
        # Send message
        await authenticated_page.fill("#text-input", test_messages["short_message"])
        await authenticated_page.click("#send-button")
        
        # Loading indicator should appear briefly
        # Note: This might be too fast to catch reliably in all cases
        loading = authenticated_page.locator("#loading-indicator")
        
        # At minimum, loading indicator should exist
        await expect(loading).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_model_selection_impact(self, authenticated_page, test_messages):
        """Test that different AI models can be selected."""
        # Change model to O3-mini
        await authenticated_page.select_option("#model-selector", "o3-mini")
        
        # Send message
        await authenticated_page.fill("#text-input", test_messages["short_message"])
        await authenticated_page.click("#send-button")
        
        # Check that model indicator updated
        await expect(authenticated_page.locator("#model-indicator")).to_contain_text("O3-MINI")
        
        # Message should still be sent successfully
        await expect(authenticated_page.locator(".user-message")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_chat_scroll_behavior(self, authenticated_page):
        """Test that chat container scrolls to show new messages."""
        # Send multiple messages to fill chat
        for i in range(5):
            await authenticated_page.fill("#text-input", f"Message {i+1}")
            await authenticated_page.click("#send-button")
            await asyncio.sleep(0.5)  # Brief delay between messages
        
        # Check that multiple messages exist
        message_count = await authenticated_page.locator(".user-message").count()
        assert message_count == 5
        
        # Last message should be visible (scrolled into view)
        last_message = authenticated_page.locator(".user-message").last
        await expect(last_message).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_voice_input_mode_switch(self, authenticated_page):
        """Test switching to voice input mode."""
        # Switch to voice input mode
        await authenticated_page.click("input[value='voice']")
        
        # Voice controls should be visible
        await expect(authenticated_page.locator("#voice-controls")).to_be_visible()
        await expect(authenticated_page.locator("#record-button")).to_be_visible()
        
        # Record button should show correct text
        await expect(authenticated_page.locator(".record-text")).to_contain_text("Start Recording")
    
    @pytest.mark.asyncio
    async def test_error_handling_display(self, authenticated_page):
        """Test error message display when errors occur."""
        error_message = authenticated_page.locator("#error-message")
        
        # Error message should initially be hidden
        await expect(error_message).to_be_hidden()
        
        # Note: Actual error triggering would require specific server conditions
        # This test verifies the error display mechanism exists