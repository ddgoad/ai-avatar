"""
User Interface Tests for AI Avatar Application

Tests all UI components and interactions as specified in the Technical Design Document.
Tests responsive design, avatar settings, input modes, and user interactions.
"""

import pytest
from playwright.async_api import expect

class TestUserInterface:
    """Test user interface components and interactions."""
    
    @pytest.mark.asyncio
    async def test_main_page_layout(self, authenticated_page):
        """Test that main page has all required components."""
        # Check header components
        await expect(authenticated_page.locator(".app-header")).to_be_visible()
        await expect(authenticated_page.locator("h1")).to_contain_text("AI Avatar Assistant")
        await expect(authenticated_page.locator("#model-selector")).to_be_visible()
        await expect(authenticated_page.locator("#logout-button")).to_be_visible()
        
        # Check main content sections
        await expect(authenticated_page.locator(".avatar-section")).to_be_visible()
        await expect(authenticated_page.locator(".chat-section")).to_be_visible()
        
        # Check input section
        await expect(authenticated_page.locator(".input-section")).to_be_visible()
        await expect(authenticated_page.locator("#text-controls")).to_be_visible()
        await expect(authenticated_page.locator("#voice-controls")).to_be_hidden()
    
    @pytest.mark.asyncio
    async def test_avatar_settings_panel(self, authenticated_page):
        """Test avatar settings panel components."""
        settings_panel = authenticated_page.locator(".avatar-settings-panel")
        await expect(settings_panel).to_be_visible()
        
        # Check all setting controls exist
        await expect(settings_panel.locator("#avatar-character")).to_be_visible()
        await expect(settings_panel.locator("#avatar-style")).to_be_visible()
        await expect(settings_panel.locator("#avatar-voice")).to_be_visible()
        await expect(settings_panel.locator("#avatar-background")).to_be_visible()
        await expect(settings_panel.locator("#avatar-gesture")).to_be_visible()
        await expect(settings_panel.locator("#video-quality")).to_be_visible()
        
        # Check that selectors have options
        character_options = await settings_panel.locator("#avatar-character option").count()
        assert character_options > 0
    
    @pytest.mark.asyncio
    async def test_input_mode_toggle(self, authenticated_page):
        """Test switching between text and voice input modes."""
        # Initially should be in text mode
        await expect(authenticated_page.locator("#text-controls")).to_be_visible()
        await expect(authenticated_page.locator("#voice-controls")).to_be_hidden()
        
        # Switch to voice mode
        await authenticated_page.click("input[value='voice']")
        
        # Voice controls should now be visible
        await expect(authenticated_page.locator("#voice-controls")).to_be_visible()
        await expect(authenticated_page.locator("#text-controls")).to_be_hidden()
        
        # Switch back to text mode
        await authenticated_page.click("input[value='text']")
        
        # Text controls should be visible again
        await expect(authenticated_page.locator("#text-controls")).to_be_visible()
        await expect(authenticated_page.locator("#voice-controls")).to_be_hidden()
    
    @pytest.mark.asyncio
    async def test_model_selector(self, authenticated_page):
        """Test AI model selection dropdown."""
        model_selector = authenticated_page.locator("#model-selector")
        await expect(model_selector).to_be_visible()
        
        # Check initial selection
        initial_value = await model_selector.input_value()
        assert initial_value in ["gpt4o", "o3-mini"]
        
        # Change model selection
        await model_selector.select_option("o3-mini")
        
        # Check that indicator updates
        await expect(authenticated_page.locator("#model-indicator")).to_contain_text("O3-MINI")
    
    @pytest.mark.asyncio
    async def test_text_input_interface(self, authenticated_page):
        """Test text input interface components."""
        # Check text input elements
        await expect(authenticated_page.locator("#text-input")).to_be_visible()
        await expect(authenticated_page.locator("#send-button")).to_be_visible()
        
        # Test typing in text area
        await authenticated_page.fill("#text-input", "Test message")
        value = await authenticated_page.locator("#text-input").input_value()
        assert value == "Test message"
        
        # Test placeholder text
        await authenticated_page.fill("#text-input", "")
        placeholder = await authenticated_page.locator("#text-input").get_attribute("placeholder")
        assert "Type your message" in placeholder
    
    @pytest.mark.asyncio
    async def test_voice_input_interface(self, authenticated_page):
        """Test voice input interface components."""
        # Switch to voice mode
        await authenticated_page.click("input[value='voice']")
        
        # Check voice input elements
        await expect(authenticated_page.locator("#audio-visualizer")).to_be_visible()
        await expect(authenticated_page.locator("#record-button")).to_be_visible()
        await expect(authenticated_page.locator(".recording-instructions")).to_be_visible()
        
        # Check record button text
        await expect(authenticated_page.locator(".record-text")).to_contain_text("Start Recording")
    
    @pytest.mark.asyncio
    async def test_avatar_video_player(self, authenticated_page):
        """Test avatar video player component."""
        video_player = authenticated_page.locator("#avatar-video")
        await expect(video_player).to_be_visible()
        
        # Check video element attributes
        controls = await video_player.get_attribute("controls")
        assert controls is not None
        
        # Check video loading overlay
        await expect(authenticated_page.locator("#video-loading")).to_be_hidden()
    
    @pytest.mark.asyncio
    async def test_chat_container(self, authenticated_page):
        """Test chat container and message display."""
        chat_container = authenticated_page.locator("#chat-container")
        await expect(chat_container).to_be_visible()
        
        # Initially should be empty
        messages = await chat_container.locator(".message").count()
        assert messages == 0
    
    @pytest.mark.asyncio
    async def test_conversation_controls(self, authenticated_page):
        """Test conversation management controls."""
        # Check control buttons exist
        await expect(authenticated_page.locator("#clear-conversation")).to_be_visible()
        await expect(authenticated_page.locator("#export-conversation")).to_be_visible()
        
        # Check button text
        await expect(authenticated_page.locator("#clear-conversation")).to_contain_text("Clear Chat")
        await expect(authenticated_page.locator("#export-conversation")).to_contain_text("Export")
    
    @pytest.mark.asyncio
    async def test_error_message_display(self, authenticated_page):
        """Test error message display functionality."""
        error_message = authenticated_page.locator("#error-message")
        
        # Error message should initially be hidden
        await expect(error_message).to_be_hidden()
    
    @pytest.mark.asyncio
    async def test_loading_indicator(self, authenticated_page):
        """Test loading indicator display."""
        loading_indicator = authenticated_page.locator("#loading-indicator")
        
        # Loading indicator should initially be hidden
        await expect(loading_indicator).to_be_hidden()
        
        # Check spinner and text
        await expect(loading_indicator.locator(".spinner")).to_be_visible()
        await expect(loading_indicator).to_contain_text("Processing your request")
    
    @pytest.mark.asyncio
    async def test_responsive_design_mobile(self, authenticated_page):
        """Test responsive design on mobile viewport."""
        # Set mobile viewport
        await authenticated_page.set_viewport_size({"width": 375, "height": 667})
        
        # Check that main elements are still visible and properly laid out
        await expect(authenticated_page.locator(".app-header")).to_be_visible()
        await expect(authenticated_page.locator(".main-content")).to_be_visible()
        await expect(authenticated_page.locator(".input-section")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_responsive_design_tablet(self, authenticated_page):
        """Test responsive design on tablet viewport."""
        # Set tablet viewport
        await authenticated_page.set_viewport_size({"width": 768, "height": 1024})
        
        # Check layout adapts properly
        await expect(authenticated_page.locator(".app-header")).to_be_visible()
        await expect(authenticated_page.locator(".avatar-section")).to_be_visible()
        await expect(authenticated_page.locator(".chat-section")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_keyboard_navigation(self, authenticated_page):
        """Test keyboard navigation and accessibility."""
        # Tab through form elements
        await authenticated_page.keyboard.press("Tab")
        
        # Check that focus moves to interactive elements
        focused_element = await authenticated_page.locator(":focus").get_attribute("id")
        assert focused_element in ["model-selector", "logout-button", "text-input", "send-button"]
    
    @pytest.mark.asyncio
    async def test_avatar_settings_interaction(self, authenticated_page, avatar_settings):
        """Test avatar settings interaction and preview updates."""
        # Change character setting
        await authenticated_page.select_option("#avatar-character", avatar_settings["character"])
        
        # Change style setting
        await authenticated_page.select_option("#avatar-style", avatar_settings["style"])
        
        # Check that preview updates (when available)
        preview = authenticated_page.locator("#avatar-preview")
        await expect(preview).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_fullscreen_toggle(self, authenticated_page):
        """Test fullscreen toggle functionality."""
        fullscreen_button = authenticated_page.locator("#fullscreen-toggle")
        
        # Button should be visible
        await expect(fullscreen_button).to_be_visible()
        await expect(fullscreen_button).to_contain_text("Fullscreen")