#!/bin/bash

echo "🚀 Setting up AI Avatar development environment..."

# Set the workspace folder name dynamically
WORKSPACE_NAME=$(basename "/workspaces/$(ls /workspaces/ | head -1)")
WORKSPACE_PATH="/workspaces/$WORKSPACE_NAME"

echo "📁 Working in: $WORKSPACE_PATH"

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -qq

# Ensure pip is up to date
echo "🐍 Updating pip and essential tools..."
python -m pip install --upgrade pip setuptools wheel

# Install Python requirements
echo "📚 Installing Python requirements..."
if [ -f "$WORKSPACE_PATH/requirements.txt" ]; then
    pip install -r "$WORKSPACE_PATH/requirements.txt"
    echo "✅ Main requirements successfully installed!"
else
    echo "⚠️  Warning: requirements.txt file not found at $WORKSPACE_PATH/requirements.txt"
fi

# Install development requirements
echo "🛠️  Installing development requirements..."
if [ -f "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt" ]; then
    pip install -r "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt"
    echo "✅ Development requirements successfully installed!"
else
    echo "⚠️  Warning: requirements-dev.txt file not found"
fi

# Verify CLI tools installation
echo "☁️  Verifying Azure CLI..."
if command -v az &> /dev/null; then
    az version
    echo "✅ Azure CLI successfully installed"
    
    # Install useful Azure CLI extensions
    echo "🔧 Installing Azure CLI extensions..."
    az extension add --name ai-examples --only-show-errors 2>/dev/null || echo "ℹ️  AI examples extension already installed or not available"
    az extension add --name azure-devops --only-show-errors 2>/dev/null || echo "ℹ️  Azure DevOps extension already installed or not available"
    
    # Check if user is logged in
    if az account show &>/dev/null; then
        echo "✅ Azure CLI is authenticated"
        az account show --query "{subscriptionId:id, name:name, user:user.name}" -o table
    else
        echo "ℹ️  Azure CLI not authenticated. Run 'az login' to authenticate."
    fi
else
    echo "❌ Azure CLI not found"
fi

echo "🔧 Verifying Azure Developer CLI..."
if command -v azd &> /dev/null; then
    azd version
    echo "✅ Azure Developer CLI successfully installed"
    
    # Check AZD authentication
    if azd auth show &>/dev/null; then
        echo "✅ Azure Developer CLI is authenticated"
    else
        echo "ℹ️  Azure Developer CLI not authenticated. Run 'azd auth login' to authenticate."
    fi
else
    echo "❌ Azure Developer CLI not found"
fi

echo "🐙 Verifying GitHub CLI..."
if command -v gh &> /dev/null; then
    gh version
    echo "✅ GitHub CLI successfully installed"
    
    # Check GitHub authentication
    if gh auth status &>/dev/null; then
        echo "✅ GitHub CLI is authenticated"
    else
        echo "ℹ️  GitHub CLI not authenticated. Run 'gh auth login' to authenticate."
    fi
else
    echo "❌ GitHub CLI not found"
fi

# Set up Git configuration placeholders
echo "🔧 Setting up Git configuration..."
if [ -z "$(git config --global user.name)" ]; then
    echo "ℹ️  Git user.name not set. Set it with: git config --global user.name 'Your Name'"
fi
if [ -z "$(git config --global user.email)" ]; then
    echo "ℹ️  Git user.email not set. Set it with: git config --global user.email 'your.email@example.com'"
fi

# Create project directory structure
echo "📁 Creating AI Avatar project directories..."
mkdir -p "$WORKSPACE_PATH/src"
mkdir -p "$WORKSPACE_PATH/src/api"
mkdir -p "$WORKSPACE_PATH/src/avatar"
mkdir -p "$WORKSPACE_PATH/src/speech"
mkdir -p "$WORKSPACE_PATH/src/utils"
mkdir -p "$WORKSPACE_PATH/tests"
mkdir -p "$WORKSPACE_PATH/docs"
mkdir -p "$WORKSPACE_PATH/static"
mkdir -p "$WORKSPACE_PATH/static/css"
mkdir -p "$WORKSPACE_PATH/static/js"
mkdir -p "$WORKSPACE_PATH/static/assets"
mkdir -p "$WORKSPACE_PATH/templates"
mkdir -p "$WORKSPACE_PATH/logs"
mkdir -p "$WORKSPACE_PATH/scripts"
mkdir -p "$WORKSPACE_PATH/configs"

# Make Azure setup script executable
if [ -f "$WORKSPACE_PATH/scripts/azure_setup.sh" ]; then
    chmod +x "$WORKSPACE_PATH/scripts/azure_setup.sh"
fi

# Set Python path
echo "🐍 Setting Python path..."
export PYTHONPATH="$WORKSPACE_PATH:$PYTHONPATH"
echo "export PYTHONPATH=\"$WORKSPACE_PATH:\$PYTHONPATH\"" >> ~/.bashrc

# Create sample configuration files
if [ ! -f "$WORKSPACE_PATH/.env" ]; then
    echo "📝 Creating sample .env file..."
    cat > "$WORKSPACE_PATH/.env" << EOF
# Azure AI Services Configuration
AZURE_SUBSCRIPTION_ID=
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_RESOURCE_GROUP=

# Azure Speech Services Configuration
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
AZURE_SPEECH_ENDPOINT=

# Azure Storage (optional - for storing generated content)
AZURE_STORAGE_ACCOUNT_NAME=
AZURE_STORAGE_ACCOUNT_KEY=
AZURE_STORAGE_CONTAINER_NAME=aiavatar-content

# Azure Key Vault (optional - for secure secret management)
AZURE_KEYVAULT_URL=

# AI Avatar Configuration
AVATAR_CHARACTER=lisa
AVATAR_STYLE=graceful-sitting
AVATAR_BACKGROUND_COLOR=#FFFFFFFF
TTS_VOICE=en-US-JennyNeural
TTS_RATE=0
TTS_PITCH=0

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_SECRET_KEY=your-secret-key-here
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
fi

# Create basic project structure files
if [ ! -f "$WORKSPACE_PATH/pyproject.toml" ]; then
    echo "📝 Creating pyproject.toml..."
    cat > "$WORKSPACE_PATH/pyproject.toml" << EOF
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-avatar"
version = "0.1.0"
description = "AI Avatar using Azure AI Services Text-to-Speech Avatar with Flask"
authors = [{name = "AI Avatar Team"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Framework :: Flask",
]

[project.urls]
Homepage = "https://github.com/yourusername/ai-avatar"
Documentation = "https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/what-is-text-to-speech-avatar"
Repository = "https://github.com/yourusername/ai-avatar"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
EOF
fi

# Create a basic README if it doesn't exist
if [ ! -f "$WORKSPACE_PATH/README.md" ]; then
    echo "📝 Creating README.md..."
    cat > "$WORKSPACE_PATH/README.md" << EOF
# AI Avatar - Azure AI Services Text-to-Speech Avatar

A Flask-based web application that integrates with Azure AI Services to create interactive text-to-speech avatars using Azure's Text-to-Speech Avatar service.

## Features

- 🤖 AI-powered text-to-speech avatars using Azure AI Services
- 🎭 Multiple avatar characters and styles
- �️ Natural voice synthesis with customizable speech parameters
- 🌐 Web-based interface built with Flask
- ☁️ Azure AI Services integration
- 🎨 Customizable avatar appearance and backgrounds

## Quick Start

1. Copy \`.env.example\` to \`.env\` and configure your Azure keys
2. Install dependencies: \`pip install -r requirements.txt\`
3. Run the Flask app: \`python src/app.py\`
4. Open your browser to \`http://localhost:5000\`

## Development

This project uses a dev container for consistent development environments.
Open in VS Code and select "Reopen in Container" when prompted.

## Configuration

Configure your Azure AI Services in the \`.env\` file:
- \`AZURE_SPEECH_KEY\` - Your Azure Speech Services key
- \`AZURE_SPEECH_REGION\` - Your Azure Speech Services region
- \`AVATAR_CHARACTER\` - Avatar character (e.g., lisa, anna)
- \`TTS_VOICE\` - Voice to use (e.g., en-US-JennyNeural)

## Architecture

- \`src/api/\` - Flask API endpoints
- \`src/avatar/\` - Avatar management and configuration
- \`src/speech/\` - Azure Speech Services integration
- \`src/utils/\` - Utility functions and helpers
- \`templates/\` - HTML templates
- \`static/\` - CSS, JavaScript, and assets

## Azure AI Services

This project uses Azure AI Services Text-to-Speech Avatar:
- [Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/what-is-text-to-speech-avatar)
- [API Reference](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/text-to-speech-avatar-quickstart)

## License

MIT License
EOF
fi

echo "✨ AI Avatar development environment setup complete!"
echo ""
echo "🔗 Quick start commands:"
echo "  - Install requirements: pip install -r requirements.txt"
echo "  - Run Flask app: python src/app.py"
echo "  - Test Azure connection: python scripts/test_speech.py"
echo "  - Run tests: pytest"
echo "  - Format code: black ."
echo "  - Type check: mypy src/"
echo ""
echo "☁️  Azure CLI commands:"
echo "  - Login to Azure: az login"
echo "  - Set subscription: az account set --subscription 'your-subscription-id'"
echo "  - Login to AZD: azd auth login"
echo "  - Initialize AZD project: azd init"
echo "  - Azure setup helper: bash scripts/azure_setup.sh"
echo ""
echo "📖 Next steps:"
echo "  - Configure your .env file with Azure AI Services keys"
echo "  - Authenticate with Azure CLI: az login"
echo "  - Authenticate with Azure Developer CLI: azd auth login"
echo "  - Review the project structure in src/ directory"
echo "  - Check out Azure Text-to-Speech Avatar documentation"
echo "  - Set up Git configuration if needed"
echo ""
echo "🎯 Ready to build your AI Avatar application!"