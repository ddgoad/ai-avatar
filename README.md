# AI Avatar Application

A comprehensive Flask-based AI Avatar application that integrates Azure Text-to-Speech Avatar service with Azure OpenAI for intelligent conversational experiences. Built with real-time WebRTC avatar streaming, Azure Container Apps deployment, and comprehensive avatar customization using Azure-validated character and style combinations.

## 🎯 Features

- **Dual Input Modes**: Text and voice input with real-time processing
- **AI Conversation**: GPT-4o and O3-mini model selection for intelligent responses with API version 2024-12-01-preview
- **Real-Time Avatar Streaming**: WebRTC-based avatar video streaming with Azure-validated configurations:
  - **Characters**: Lisa, Harry, Jeff, Lori, Meg, Max (Azure Speech SDK validated)
  - **Styles**: Character-specific real-time compatible styles (Lisa: casual-sitting only)
  - **Voices**: 400+ Azure Neural Voices with filtering
  - **Backgrounds**: Solid colors, custom images, transparent
  - **Gestures**: Wave, nod, thumbs-up, point via SSML
  - **Quality**: 720p/1080p video output
- **Azure Container Apps**: Serverless deployment with auto-scaling and managed identity
- **Authentication**: Simple form-based authentication
- **Conversation Management**: History, export, and clear functionality
- **Responsive Design**: Mobile and desktop compatibility

## 🚀 Quick Start with Azure Developer CLI (AZD)

### Prerequisites

- **Azure Subscription** with permissions to create resources
- **Azure CLI** installed and authenticated
- **Azure Developer CLI (AZD)** installed
- **Docker** (for container operations)
- **Git** (for repository cloning)

### 1. Install Required Tools

```bash
# Install Azure CLI (if not already installed)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash

# Verify installations
az version
azd version
```

### 2. Clone and Initialize

```bash
# Clone the repository
git clone https://github.com/ddgoad/ai-avatar.git
cd ai-avatar

# Initialize AZD environment
azd init
```

### 3. Configure Azure Services

Before deployment, ensure you have:
- **Azure OpenAI** resource with GPT-4o and O3-mini deployments
- **Azure Speech Services** resource (S0 tier recommended)

### 4. Deploy with AZD

```bash
# Authenticate with Azure
azd auth login

# Set deployment location (choose region with OpenAI availability)
azd env set AZURE_LOCATION "eastus2"

# Configure OpenAI settings
azd env set AZURE_OPENAI_ENDPOINT "https://your-openai-resource.openai.azure.com/"
azd env set AZURE_OPENAI_GPT4O_DEPLOYMENT "your-gpt4o-deployment-name"
azd env set AZURE_OPENAI_O3_MINI_DEPLOYMENT "your-o3mini-deployment-name"

# Configure Speech Services
azd env set AZURE_SPEECH_REGION "eastus2"

# Deploy infrastructure and application
azd up
```

The `azd up` command will:
1. 🏗️ **Provision Azure Resources**: Container Apps, Key Vault, Storage, Application Insights
2. 🐳 **Build Container Image**: Docker build and push to Azure Container Registry
3. 🚀 **Deploy Application**: Deploy to Azure Container Apps with managed identity
4. 🔧 **Configure Secrets**: Securely store credentials in Key Vault
5. 📊 **Setup Monitoring**: Configure Application Insights and logging

### 5. Access Your Application

After successful deployment, AZD will provide the application URL:
```
Your application is available at: https://your-app-name.azurecontainerapps.io
```

### 6. Manage and Monitor

```bash
# Check application status
azd show

# View application logs
azd logs

# Monitor in Azure portal
azd show --output json | jq -r '.services.web.resourceName'

# Update environment variables
azd env set NEW_VARIABLE "value"
azd deploy  # Apply changes
```

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- Azure subscription with configured services

### Setup

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

4. **Configure environment variables**
   Create a `.env` file with your Azure service credentials:
   ```bash
   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-openai-key
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   AZURE_OPENAI_GPT4O_DEPLOYMENT=your-gpt4o-deployment
   AZURE_OPENAI_O3_MINI_DEPLOYMENT=your-o3mini-deployment

   # Azure Speech Services Configuration
   AZURE_SPEECH_KEY=your-speech-key
   AZURE_SPEECH_REGION=eastus2

   # Application Configuration
   FLASK_SECRET_KEY=your-secret-key
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

## � Troubleshooting

### Common Issues

#### 1. O3-mini Model Not Found
**Error**: `Connection Error: Model o3-mini is enabled only for api versions 2024-12-01-preview and later`

**Solution**: Ensure you're using the correct API version:
```bash
azd env set AZURE_OPENAI_API_VERSION "2024-12-01-preview"
azd deploy
```

#### 2. Avatar Configuration Lockup
**Error**: Avatar interface becomes unresponsive when changing character/style

**Solution**: The application now uses Azure-validated character/style combinations. Lisa only supports 'casual-sitting' for real-time synthesis.

#### 3. WebRTC Connection Issues
**Error**: Avatar video not streaming

**Solution**: Check browser permissions for camera/microphone and ensure HTTPS is enabled in production.

#### 4. Deployment Failures
**Error**: AZD deployment fails

**Solution**: 
```bash
# Check Azure CLI authentication
az account show

# Verify permissions
az group list

# Check resource availability in your region
azd env set AZURE_LOCATION "eastus2"
```

#### 5. Container App Start Issues
**Error**: Application fails to start

**Solution**: Check Application Insights logs:
```bash
azd logs --follow
```

### Getting Help

- **Documentation**: See `docs/technical-design-document.md` for detailed architecture
- **Azure Support**: Use Azure portal for service-specific issues
- **GitHub Issues**: Report bugs and request features
- **Logs**: Use `azd logs` for deployment debugging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support Resources

- **Azure OpenAI**: [Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- **Azure Speech Services**: [Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)
- **Azure Container Apps**: [Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- **Azure Developer CLI**: [Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)

## 🙏 Acknowledgments

- **Azure AI Services**: For powerful speech and OpenAI capabilities
- **Microsoft**: For Azure Container Apps platform
- **Azure Developer CLI**: For streamlined deployment automation
- **Open Source Community**: For excellent Python and web frameworks

---

**Built with** ❤️ **using Azure AI Services, Container Apps, and Developer CLI**

