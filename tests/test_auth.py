"""
Authentication Tests for AI Avatar Application

Tests the authentication system exactly as specified in the Technical Design Document.
Tests login/logout functionality with specified credentials: UTASAvatar/UTASRocks!
"""

import pytest
from playwright.async_api import expect
import asyncio

class TestAuthentication:
    """Test authentication functionality."""
    
    @pytest.mark.asyncio
    async def test_login_page_loads(self, page):
        """Test that login page loads correctly."""
        await page.goto("http://localhost:5000/login")
        
        # Check page title
        await expect(page).to_have_title("AI Avatar Login")
        
        # Check login form elements exist
        await expect(page.locator("#username")).to_be_visible()
        await expect(page.locator("#password")).to_be_visible()
        await expect(page.locator("#login-button")).to_be_visible()
        
        # Check demo credentials are displayed
        await expect(page.locator("text=UTASAvatar")).to_be_visible()
        await expect(page.locator("text=UTASRocks!")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_successful_login(self, page, test_credentials):
        """Test successful login with correct credentials."""
        await page.goto("http://localhost:5000/login")
        
        # Fill in valid credentials
        await page.fill("#username", test_credentials["valid_username"])
        await page.fill("#password", test_credentials["valid_password"])
        
        # Submit login form
        await page.click("#login-button")
        
        # Should redirect to main application
        await page.wait_for_url("http://localhost:5000/")
        await expect(page).to_have_title("AI Avatar Chat")
        
        # Check that main app elements are visible
        await expect(page.locator(".app-header")).to_be_visible()
        await expect(page.locator("text=AI Avatar Assistant")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_failed_login_invalid_username(self, page, test_credentials):
        """Test failed login with invalid username."""
        await page.goto("http://localhost:5000/login")
        
        # Fill in invalid username
        await page.fill("#username", test_credentials["invalid_username"])
        await page.fill("#password", test_credentials["valid_password"])
        
        # Submit login form
        await page.click("#login-button")
        
        # Should stay on login page and show error
        await expect(page.locator("#error-message")).to_be_visible()
        await expect(page.locator("#error-message")).to_contain_text("Invalid credentials")
        
        # Should still be on login page
        await expect(page).to_have_url("http://localhost:5000/login")
    
    @pytest.mark.asyncio
    async def test_failed_login_invalid_password(self, page, test_credentials):
        """Test failed login with invalid password."""
        await page.goto("http://localhost:5000/login")
        
        # Fill in invalid password
        await page.fill("#username", test_credentials["valid_username"])
        await page.fill("#password", test_credentials["invalid_password"])
        
        # Submit login form
        await page.click("#login-button")
        
        # Should show error message
        await expect(page.locator("#error-message")).to_be_visible()
        await expect(page.locator("#error-message")).to_contain_text("Invalid credentials")
    
    @pytest.mark.asyncio
    async def test_failed_login_empty_fields(self, page):
        """Test failed login with empty fields."""
        await page.goto("http://localhost:5000/login")
        
        # Submit without filling fields
        await page.click("#login-button")
        
        # Form validation should prevent submission
        username_field = page.locator("#username")
        await expect(username_field).to_be_focused()
    
    @pytest.mark.asyncio
    async def test_logout_functionality(self, authenticated_page):
        """Test logout functionality."""
        # Should be on main page after authentication
        await expect(authenticated_page).to_have_url("http://localhost:5000/")
        
        # Click logout button
        await authenticated_page.click("#logout-button")
        
        # Should redirect to login page
        await authenticated_page.wait_for_url("http://localhost:5000/login")
        await expect(authenticated_page).to_have_title("AI Avatar Login")
    
    @pytest.mark.asyncio
    async def test_protected_route_access(self, page):
        """Test that protected routes redirect to login."""
        # Try to access main page without authentication
        await page.goto("http://localhost:5000/")
        
        # Should redirect to login page
        await page.wait_for_url("http://localhost:5000/login")
        await expect(page).to_have_title("AI Avatar Login")
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, authenticated_page):
        """Test that session persists across page reloads."""
        # Should be authenticated
        await expect(authenticated_page).to_have_url("http://localhost:5000/")
        
        # Reload page
        await authenticated_page.reload()
        
        # Should still be on main page (not redirected to login)
        await expect(authenticated_page).to_have_url("http://localhost:5000/")
        await expect(authenticated_page.locator(".app-header")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_login_form_autofill(self, page):
        """Test that login form is pre-filled with demo credentials."""
        await page.goto("http://localhost:5000/login")
        
        # Check that demo credentials are pre-filled
        username_value = await page.locator("#username").input_value()
        password_value = await page.locator("#password").input_value()
        
        assert username_value == "UTASAvatar"
        assert password_value == "UTASRocks!"
    
    @pytest.mark.asyncio
    async def test_login_loading_state(self, page, test_credentials):
        """Test login button loading state during submission."""
        await page.goto("http://localhost:5000/login")
        
        # Fill in credentials
        await page.fill("#username", test_credentials["valid_username"])
        await page.fill("#password", test_credentials["valid_password"])
        
        # Click login and immediately check loading state
        await page.click("#login-button")
        
        # Button should be disabled during loading
        await expect(page.locator("#login-button")).to_be_disabled()
        
        # Spinner should be visible
        await expect(page.locator("#login-spinner")).to_be_visible()