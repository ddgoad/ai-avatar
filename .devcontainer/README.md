# AI Avatar Dev Container

This dev container provides a complete development environment for the AI Avatar project, optimized for Azure AI Services Text-to-Speech Avatar development with Flask and Python.

## Features

### Base Environment
- **Python 3.11** with latest pip, setuptools, and wheel
- **Ubuntu/Debian** based container with audio/video processing dependencies
- **Docker-in-Docker** support for containerization tasks

### Development Tools
- **Azure CLI** - Azure command-line interface
- **Azure Developer CLI (azd)** - Modern Azure deployment tool
- **GitHub CLI** - GitHub command-line interface
- **Node.js LTS** - For frontend tooling and build processes

### AI Avatar Stack
- **Azure Speech Services** - Text-to-speech and avatar services
- **Flask** - Python web framework for API development
- **Audio Processing** - FFmpeg and related tools for media handling
- **Transformers** - HuggingFace model library
- **Sentence Transformers** - Text embedding models
- **Multiple Vector Databases** - ChromaDB, FAISS, Pinecone, Weaviate, Qdrant
- **spaCy & NLTK** - Natural language processing

### Web Frameworks & APIs
- **Flask** - Lightweight web framework for building web applications
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **Flask-SocketIO** - WebSocket support for real-time features

### Azure Integration
- **Azure SDK** - Complete Azure service integration
- **Azure Speech Services** - Text-to-speech and avatar services
- **Azure Cognitive Services** - AI/ML services integration
- **Azure Identity** - Authentication and authorization
- **Azure Key Vault** - Secrets management (optional)
- **Azure Monitor** - Logging and telemetry (optional)

### Audio & Media Processing
- **PyDub** - Audio manipulation library
- **NumPy** - Numerical computing for audio processing
- **FFmpeg** - Multimedia processing framework

### Development & Testing
- **pytest** - Advanced testing framework with Flask support
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Code linting
- **mypy** - Type checking and static analysis
- **pre-commit** - Git hooks for code quality

## Quick Start

1. **Open in VS Code**: Open this folder in VS Code and click "Reopen in Container" when prompted.

2. **Wait for Setup**: The container will build and run the startup script automatically.

3. **Configure Environment**: 
   - Edit `.env` file with your Azure AI Services keys and configuration
   - Set up Git configuration if needed:
     ```bash
     git config --global user.name "Your Name"
     git config --global user.email "your.email@example.com"
     ```

4. **Start Development**: Your environment is ready! Common commands:
   ```bash
   # Run Flask application
   python src/app.py
   
   # Run with Flask CLI
   flask run --host=0.0.0.0 --port=5000
   
   # Run tests
   pytest
   
   # Format code
   black . && isort .
   
   # Type check
   mypy src/
   
   # Install additional packages
   pip install package-name
   ```

## Project Structure

The startup script creates the following AI Avatar project structure:
```
ai-avatar/
├── src/
│   ├── api/          # Flask API endpoints
│   ├── avatar/       # Avatar management and configuration
│   ├── speech/       # Azure Speech Services integration
│   └── utils/        # Utility functions and helpers
├── tests/            # Test files
├── docs/             # Documentation
├── static/           # Static web assets
│   ├── css/          # Stylesheets
│   ├── js/           # JavaScript files
│   └── assets/       # Images, fonts, etc.
├── templates/        # HTML templates
├── logs/             # Application logs
├── scripts/          # Utility scripts
└── configs/          # Configuration files
```

## Azure AI Services Support

Pre-configured for Azure AI Services:
- **Azure Speech Services** - Text-to-speech and avatar functionality
- **Azure Cognitive Services** - Additional AI capabilities
- **Azure Identity** - Secure authentication

## Avatar Configuration

Support for various avatar options:
- **Characters** - lisa, anna, etc.
- **Styles** - graceful-sitting, standing, etc.
- **Voices** - Multiple neural voices in different languages
- **Customization** - Background colors, speech parameters

## Azure Deployment Ready

This container is optimized for Azure deployment:
- Azure Container Apps support
- Azure App Service compatibility  
- Pre-configured Azure tools and SDKs
- Environment variable and secrets management
- Azure Monitor integration (optional)

## Ports

The following ports are forwarded:
- `5000` - Flask application server
- `8000` - Alternative server port
- `8080` - Development server
- `3000` - Frontend development server
- `7860` - Gradio interface

## Volume Mounts and Caching

Optimized for AI Avatar development:
- Workspace files mounted at `/workspaces/`
- Docker socket forwarded for container operations
- Pip cache persisted across rebuilds
- Azure CLI cache persisted

## Environment Configuration

Key environment variables for AI Avatar:
- **AZURE_SPEECH_KEY** - Azure Speech Services API key
- **AZURE_SPEECH_REGION** - Azure Speech Services region
- **AVATAR_CHARACTER** - Avatar character selection
- **TTS_VOICE** - Text-to-speech voice selection
- **FLASK_SECRET_KEY** - Flask application secret

## Customization

- **Add Azure services**: Update `requirements.txt` with new Azure SDK packages
- **Add avatar features**: Extend the avatar directory
- **Add API endpoints**: Extend the api directory
- **Add VS Code extensions**: Update `devcontainer.json`
- **Add system packages**: Update `Dockerfile`
- **Modify startup**: Update `startup.sh`

## Development Workflow

Recommended development workflow:
1. Configure `.env` with your Azure AI Services keys
2. Test Azure Speech Services connection: `python scripts/test_speech.py`
3. Test avatar functionality: `python scripts/test_avatar.py`
4. Launch Flask application: `python src/app.py`
5. Access web interface at `http://localhost:5000`

## Troubleshooting

### Azure Authentication Issues
To authenticate with Azure:
```bash
az login
az account set --subscription "your-subscription-id"
```

### Speech Services Connection
For Azure Speech Services issues:
```bash
# Verify your region and key
echo $AZURE_SPEECH_REGION
echo $AZURE_SPEECH_KEY
```

### Flask Application Issues
For Flask development:
```bash
# Run in debug mode
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=5000
```

## Performance Optimization

The container includes several optimizations:
- Persistent caches for packages and Azure CLI
- Audio processing libraries for efficient media handling
- Optimized Flask configuration for development
- WebSocket support for real-time features

## Contributing

When adding new dependencies:
1. Add to `requirements.txt` for production dependencies
2. Add to `.devcontainer/requirements-dev.txt` for development-only dependencies
3. Update this README if adding new major features
4. Rebuild the container to test changes

For AI Avatar specific contributions:
- Test with different avatar characters and styles
- Verify speech synthesis quality with various voices
- Ensure web interface responsiveness
- Test real-time features and WebSocket connections
