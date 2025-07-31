# AI Avatar Application

A comprehensive Flask-based AI Avatar application that integrates Azure Text-to-Speech Avatar service with Azure OpenAI for intelligent conversational experiences. Built following the Technical Design Document specifications with dual input support (text/voice), Azure Container Apps deployment, and comprehensive avatar customization.

## 🎯 Features

- **Dual Input Modes**: Text and voice input with real-time processing
- **AI Conversation**: GPT-4o and O3-mini model selection for intelligent responses
- **Avatar Customization**: Complete avatar personalization with:
  - Characters: Lisa, Mark, Anna, Jenny, Ryan
  - Styles: graceful-sitting, standing, casual, professional
  - Voices: 400+ Azure Neural Voices with filtering
  - Backgrounds: solid colors, custom images, transparent
  - Gestures: wave, nod, thumbs-up, point via SSML
  - Quality: 720p/1080p video output
- **Azure Container Apps**: Serverless deployment with auto-scaling
- **Authentication**: Simple form-based authentication
- **Conversation Management**: History, export, and clear functionality
- **Responsive Design**: Mobile and desktop compatibility

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure subscription with:
  - Azure Speech Services (S0 tier)
  - Azure OpenAI with GPT-4o and O3-mini deployments
  - Azure Container Apps (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ddgoad/ai-avatar.git
   cd ai-avatar
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure service keys
   ```

5. **Run the application**
   ```bash
   export PYTHONPATH=/path/to/ai-avatar
   python src/app.py
   ```

6. **Access the application**
   - Open browser to `http://localhost:5000`
   - Login with credentials: `UTASAvatar` / `UTASRocks!`

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Azure Speech Services
AZURE_SPEECH_KEY=your_speech_service_key
AZURE_SPEECH_REGION=eastus2

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_GPT4O_DEPLOYMENT=gpt-4o
AZURE_OPENAI_O3_MINI_DEPLOYMENT=o3-mini

# Flask Application
FLASK_SECRET_KEY=your-secret-key-for-sessions
FLASK_ENV=production
```

### Avatar Settings

Customize default avatar appearance:

```bash
AVATAR_CHARACTER=lisa
AVATAR_STYLE=graceful-sitting
TTS_VOICE=en-US-JennyNeural
AVATAR_BACKGROUND_COLOR=#FFFFFF
```

## 🏗️ Architecture

The application follows a clean architecture with clear separation of concerns:

- **Authentication Module** (`src/auth/`): Simple form-based authentication
- **Input Processing** (`src/input/`): Unified text/voice input handling
- **LLM Integration** (`src/llm/`): Azure OpenAI service integration
- **Avatar Management** (`src/avatar/`): Avatar customization and video generation
- **Speech Services** (`src/speech/`): Azure Speech-to-Text integration
- **API Routes** (`src/api/`): RESTful API endpoints
- **Frontend** (`templates/`, `static/`): Responsive web interface

## 📡 API Endpoints

### Authentication
- `POST /api/login` - User authentication
- `POST /api/logout` - User logout

### Chat Functionality
- `POST /api/chat` - Main chat endpoint (text/voice)
- `GET /api/models` - Available AI models
- `GET /api/conversation` - Get conversation history
- `DELETE /api/conversation` - Clear conversation
- `GET /api/export-conversation` - Export conversation as JSON

### Avatar Management
- `GET /api/avatar/config` - Get avatar configuration options
- `POST /api/avatar/config` - Update avatar settings
- `GET /api/video/<video_id>` - Serve avatar videos

## 🐳 Docker Deployment

### Build and Run Locally

```bash
# Build the container
docker build -t ai-avatar .

# Run the container
docker run -p 80:80 --env-file .env ai-avatar
```

### Azure Container Apps Deployment

The application is designed for Azure Container Apps deployment:

```bash
# Login to Azure
azd auth login

# Initialize environment
azd env new

# Deploy infrastructure and application
azd up
```

## 🧪 Testing

The application includes comprehensive Playwright tests covering:

- **Authentication**: Login/logout flows
- **UI Components**: All interactive elements
- **Chat Functionality**: Text/voice input processing
- **Avatar Customization**: Settings and real-time updates
- **Responsive Design**: Mobile and desktop layouts

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_auth.py -v     # Authentication tests
python -m pytest tests/test_ui.py -v      # UI component tests
python -m pytest tests/test_chat.py -v    # Chat functionality tests

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── test_auth.py               # Authentication tests
├── test_ui.py                 # UI component tests
├── test_chat.py               # Chat functionality tests
└── fixtures/                  # Test data and mock responses
```

## 🔐 Security

- **Authentication**: Simple form-based authentication with session management
- **Azure Key Vault**: Secure storage of API keys and connection strings
- **HTTPS Enforcement**: All communications encrypted in transit
- **Input Validation**: Comprehensive input sanitization
- **CORS Configuration**: Proper cross-origin resource sharing setup

## 📈 Performance

- **Auto-scaling**: Azure Container Apps handles traffic spikes automatically
- **Caching**: Avatar videos cached for improved performance
- **Optimization**: Async processing and connection pooling
- **CDN Ready**: Static assets optimized for global distribution

### Performance Targets

- Page load time: < 3 seconds
- Avatar video generation: < 10 seconds
- Voice processing: < 5 seconds
- UI responsiveness: < 200ms for interactions

## 🌍 Deployment Environments

### Development
- Single region: East US 2
- Basic tier services
- Shared resources for cost optimization

### Production
- Primary region: East US 2
- Secondary region: West US 2 (disaster recovery)
- Global CDN with Azure Front Door
- High availability configuration

## 📊 Monitoring

The application includes comprehensive monitoring:

- **Application Insights**: Real-time performance monitoring
- **Custom Metrics**: Avatar generation times and success rates
- **Health Checks**: Automated endpoint monitoring
- **Alerting**: Automated alerts for failures or performance degradation

## 🔄 CI/CD Pipeline

Automated deployment pipeline with GitHub Actions:

1. **Build**: Install dependencies and build application
2. **Test**: Run comprehensive test suite
3. **Security Scan**: Vulnerability assessment
4. **Deploy**: Deploy to Azure Container Apps
5. **Smoke Test**: Verify deployment health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding standards and write tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Follow the Technical Design Document specifications
- Write comprehensive tests for new features
- Ensure responsive design compatibility
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Technical Design Document in `docs/`
- **Issues**: GitHub Issues for bug reports and feature requests
- **Azure Support**: Azure portal for service-specific issues

## 🙏 Acknowledgments

- **Azure AI Services**: For powerful speech and OpenAI capabilities
- **Microsoft**: For Azure Container Apps platform
- **Open Source Community**: For excellent Python and web frameworks

---

**Built with** ❤️ **using Azure AI Services and Container Apps**

## Features

- 🤖 AI-powered text-to-speech avatars using Azure AI Services
- 🎭 Multiple avatar characters and styles
- �️ Natural voice synthesis with customizable speech parameters
- 🌐 Web-based interface built with Flask
- ☁️ Azure AI Services integration
- 🎨 Customizable avatar appearance and backgrounds

## Quick Start

1. Copy `.env.example` to `.env` and configure your Azure keys
2. Install dependencies: `pip install -r requirements.txt`
3. Run the Flask app: `python src/app.py`
4. Open your browser to `http://localhost:5000`

## Development

This project uses a dev container for consistent development environments.
Open in VS Code and select "Reopen in Container" when prompted.

## Configuration

Configure your Azure AI Services in the `.env` file:
- `AZURE_SPEECH_KEY` - Your Azure Speech Services key
- `AZURE_SPEECH_REGION` - Your Azure Speech Services region
- `AVATAR_CHARACTER` - Avatar character (e.g., lisa, anna)
- `TTS_VOICE` - Voice to use (e.g., en-US-JennyNeural)

## Architecture

- `src/api/` - Flask API endpoints
- `src/avatar/` - Avatar management and configuration
- `src/speech/` - Azure Speech Services integration
- `src/utils/` - Utility functions and helpers
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and assets

## Azure AI Services

This project uses Azure AI Services Text-to-Speech Avatar:
- [Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/what-is-text-to-speech-avatar)
- [API Reference](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/text-to-speech-avatar-quickstart)

## License

MIT License
