"""
Pytest configuration for AI Avatar application testing.
Sets up test environment and fixtures for Playwright tests.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright
import subprocess
import time
import os
import sys

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def flask_app():
    """Start Flask application for testing."""
    # Set test environment variables
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['FLASK_DEBUG'] = '0'
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(__file__))
    
    # Start Flask app in subprocess
    proc = subprocess.Popen([
        sys.executable, 'src/app.py'
    ], cwd=os.path.dirname(os.path.dirname(__file__)))
    
    # Wait for app to start
    time.sleep(3)
    
    yield proc
    
    # Cleanup
    proc.terminate()
    proc.wait()

@pytest.fixture(scope="session")
async def browser():
    """Create browser instance for testing."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser):
    """Create a new page for each test."""
    page = await browser.new_page()
    yield page
    await page.close()

@pytest.fixture
async def authenticated_page(page):
    """Create an authenticated page session."""
    # Navigate to login page
    await page.goto("http://localhost:5000/login")
    
    # Fill in credentials
    await page.fill("#username", "UTASAvatar")
    await page.fill("#password", "UTASRocks!")
    
    # Submit login form
    await page.click("#login-button")
    
    # Wait for redirect to main page
    await page.wait_for_url("http://localhost:5000/")
    
    yield page

# Test data fixtures
@pytest.fixture
def test_credentials():
    """Test credentials as specified in TDD."""
    return {
        "valid_username": "UTASAvatar",
        "valid_password": "UTASRocks!",
        "invalid_username": "invalid",
        "invalid_password": "invalid"
    }

@pytest.fixture
def avatar_settings():
    """Sample avatar settings for testing."""
    return {
        "character": "lisa",
        "style": "graceful-sitting", 
        "voice": "en-US-JennyNeural",
        "background": "solid-white",
        "gesture": None,
        "video_quality": "high"
    }

@pytest.fixture
def test_messages():
    """Sample test messages."""
    return {
        "short_message": "Hello!",
        "long_message": "This is a longer test message to verify that the AI Avatar application can handle extended text input and generate appropriate responses with proper avatar video synthesis.",
        "special_chars": "Hello! How are you? I'm testing special characters: @#$%^&*()",
        "multilang": "Hello! Bonjour! ¡Hola!"
    }