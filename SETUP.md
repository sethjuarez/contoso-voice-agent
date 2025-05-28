# Contoso Voice Agent - Development Setup Guide

This guide provides comprehensive instructions for setting up your development environment to run the Contoso Voice Agent project successfully.

## Project Overview

The Contoso Voice Agent is a sophisticated AI-powered voice and text assistant for Contoso Outdoors that provides personalized product recommendations and customer support through natural conversations. For detailed project information, architecture, and features, please refer to the [README.md](./README.md).

The application consists of:
- **Backend API** (Python FastAPI) - Handles AI integration, WebSocket connections, and business logic
- **Frontend Web** (Next.js TypeScript) - Provides chat and voice interfaces with real-time audio processing
- **Azure OpenAI Integration** - Powers conversations using GPT-4o and Realtime Voice API

## Prerequisites

Before setting up the project, ensure you have the following installed on your development machine:

### Required Software
- **Python 3.12+** - For the backend API
- **Node.js 18+** - For the frontend application  
- **npm or yarn** - Package manager for Node.js dependencies
- **Git** - Version control (for cloning and contributing)

### Optional but Recommended
- **Visual Studio Code** - IDE with pre-configured launch settings
- **Docker** - For containerized development and deployment
- **Azure CLI** - For deployment to Azure Container Apps

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 8GB (16GB recommended for voice processing)
- **Disk Space**: At least 2GB free space for dependencies and build artifacts

## Environment Configuration

### Azure OpenAI Setup

Before running the application, you need access to Azure OpenAI services. Create a `.env` file in the `api` directory with the following configuration:

```bash
# Create api/.env file with your Azure OpenAI credentials
# For chat functionality (GPT-4o)
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key

# For voice functionality (Realtime API)
AZURE_VOICE_ENDPOINT=your_azure_voice_endpoint
AZURE_VOICE_KEY=your_azure_voice_api_key

# Optional: Enable local tracing for development
LOCAL_TRACING_ENABLED=true
```

**Note**: 
- Replace the placeholder values with your actual Azure OpenAI service credentials
- You'll need access to both GPT-4o (for chat) and the Realtime Voice API (for voice calls)
- The chat and voice endpoints may be the same if using a unified Azure OpenAI service
- For development, you can use `LOCAL_TRACING_ENABLED=true` to enable detailed logging

## Backend API Setup

The backend is built with Python FastAPI and handles AI integration, WebSocket connections, and product recommendations.

### 1. Create Virtual Environment (Recommended)
```bash
# Create virtual environment in project root
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install backend dependencies
pip install -r api/requirements.txt
```

### 3. Set Environment Variables
Create a `.env` file in the `api` directory with your Azure OpenAI credentials (see Environment Configuration section above).

### 4. Start the Backend Server
```bash
# Run from project root directory, not from api/
uvicorn api.main:app --reload
```

The API server will start on `http://localhost:8000`. You can verify it's running by visiting `http://localhost:8000` in your browser.

### Backend Structure Overview
- `main.py` - FastAPI application entry point with WebSocket endpoints
- `models.py` - Pydantic data models for products, messages, and sessions
- `session.py` - Session management and conversation context
- `chat/` - Chat functionality and prompts
- `suggestions/` - Product recommendation engine
- `voice/` - Voice processing and Realtime API integration
- `tests/` - Unit tests and evaluation framework

## Frontend Web Setup

The frontend is built with Next.js and TypeScript, providing both chat and voice interfaces.

### 1. Navigate to Web Directory
```bash
cd web
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start the Development Server
```bash
npm run dev
```

The web application will start on `http://localhost:3000`. It will automatically connect to the backend API at `http://localhost:8000`.

### Frontend Structure Overview
- `src/app/` - Next.js App Router pages and layouts
- `src/components/` - React components for chat and voice interfaces
- `src/store/` - Zustand state management stores
- `src/audio/` - Web Audio API integration and worklets
- `src/socket/` - WebSocket client for real-time communication
- `public/` - Static assets including product images and manuals

## Running Everything Together

### Method 1: Terminal Windows
1. **Start Backend** (Terminal 1):
   ```bash
   # From project root directory
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   uvicorn api.main:app --reload
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd web
   npm run dev
   ```

3. **Access Application**: Open `http://localhost:3000` in your browser

### Method 2: VS Code (Recommended)
The project includes VS Code launch configurations for integrated development:

1. Open the project root directory in VS Code
2. Press `F5` or go to Run → Start Debugging
3. This will start both backend and frontend services automatically

### Method 3: Docker (Optional)
For containerized development:

1. **Build and run backend**:
   ```bash
   cd api
   docker build -t contoso-voice-api .
   docker run -p 8000:8000 --env-file .env contoso-voice-api
   ```

2. **Build and run frontend**:
   ```bash
   cd web
   docker build -t contoso-voice-web .
   docker run -p 3000:3000 contoso-voice-web
   ```

## Testing Your Setup

### Backend Testing
```bash
cd api
pytest
```

### Frontend Testing
```bash
cd web
npm run lint
npm run build
```

### Integration Testing
1. Open `http://localhost:3000` in your browser
2. Try the text chat interface - send a message about outdoor products
3. Test the voice interface (requires microphone permissions)
4. Verify real-time communication between frontend and backend

## Development Workflow

### Code Quality
- **Backend**: Use `pytest` for testing, follow PEP 8 style guidelines
- **Frontend**: Use `npm run lint` for ESLint checks, `npm run build` to verify builds

### Making Changes
1. Backend changes automatically reload with `python main.py`
2. Frontend changes hot-reload with `npm run dev`
3. Test both interfaces after making changes

### Environment Files
- Keep `.env` files in `.gitignore` (already configured)
- Use `.env.example` files to document required variables
- Never commit actual API keys or secrets

## GitHub Actions Deployment

The project includes automated deployment to Azure Container Apps using GitHub Actions workflows.

### Deployment Workflows

#### 1. Backend API Deployment (`.github/workflows/azure-container-api.yml`)
**Triggers:**
- Push to `main` branch with changes in `api/` directory
- Manual workflow dispatch

**Process:**
1. **Build Phase:**
   - Creates timestamp-based version tag
   - Logs into Azure using federated credentials
   - Builds Docker image from `api/Dockerfile`
   - Pushes image to Azure Container Registry

2. **Deploy Phase:**
   - Deploys container to Azure Container Apps
   - Configures environment variables from secrets:
     - `AZURE_OPENAI_ENDPOINT`
     - `AZURE_OPENAI_API_KEY` 
     - `AZURE_VOICE_ENDPOINT`
     - `AZURE_VOICE_KEY`
     - `APPINSIGHTS_CONNECTIONSTRING`
   - Sets `LOCAL_TRACING_ENABLED=false` for production
   - Exposes service on port 8000

#### 2. Frontend Web Deployment (`.github/workflows/azure-container-web.yml`)
**Triggers:**
- Push to `main` branch with changes in `web/` directory
- Manual workflow dispatch

**Process:**
1. **Configuration Phase:**
   - Retrieves API and web endpoints from existing Azure Container Apps
   - Dynamically updates `web/src/store/endpoint.ts` with production URLs
   - Updates version information in `web/src/store/version.ts`

2. **Build and Deploy Phase:**
   - Builds Docker image from `web/Dockerfile`
   - Pushes to Azure Container Registry
   - Deploys to Azure Container Apps with auto-scaling configuration
   - Sets up HTTP scaling rules (1-5 replicas, 100 concurrent requests)

### Required Secrets

For deployment to work, configure these GitHub repository secrets:

```
AZURE_CLIENT_ID          # Azure service principal client ID
AZURE_TENANT_ID          # Azure tenant ID  
AZURE_SUBSCRIPTION_ID    # Azure subscription ID
REGISTRY_ENDPOINT        # Azure Container Registry URL
REGISTRY_USERNAME        # Container registry username
REGISTRY_PASSWORD        # Container registry password
```

### Infrastructure Requirements

The deployment assumes the following Azure resources exist:
- **Resource Group**: `contoso-concierge`
- **Container Apps Environment**: `contoso-concierge-env`
- **Workload Profile**: `heavy-workload` (for API compute requirements)
- **Key Vault Secrets**: For storing API keys and connection strings

### Manual Deployment

To deploy manually:

```bash
# Trigger workflow manually
gh workflow run azure-container-api.yml
gh workflow run azure-container-web.yml

# Or push changes to main branch
git push origin main
```

## Troubleshooting

### Common Issues

#### Backend Issues
- **Port already in use**: Change port in `main.py` or kill existing process
- **Missing dependencies**: Ensure virtual environment is activated and requirements installed
- **Azure OpenAI errors**: Verify your `.env` file has correct credentials and quotas

#### Frontend Issues  
- **Node version**: Ensure Node.js 18+ is installed
- **Dependency conflicts**: Try deleting `node_modules` and running `npm install` again
- **Build errors**: Run `npm run lint` to check for TypeScript/ESLint issues

#### Audio/Voice Issues
- **Microphone permissions**: Enable microphone access in browser settings
- **WebSocket errors**: Ensure backend is running and accessible
- **Audio worklet errors**: Use a modern browser (Chrome/Firefox latest versions)

#### Development Environment
- **VS Code debugging**: Ensure Python extension is installed and virtual environment is selected
- **Hot reload not working**: Check file watchers and firewall settings
- **CORS issues**: Backend is configured for all origins in development mode

### Getting Help

1. **Check Logs**: Backend logs appear in terminal, frontend logs in browser console
2. **Test Connectivity**: Verify `http://localhost:8000` and `http://localhost:3000` are accessible
3. **Review Environment**: Double-check all environment variables are set correctly
4. **Update Dependencies**: Ensure all packages are up to date

### Performance Tips

- **Development**: Use `LOCAL_TRACING_ENABLED=true` for debugging
- **Voice Quality**: Use wired headphones to avoid audio feedback
- **Network**: Stable internet connection required for Azure OpenAI API calls
- **Browser**: Chrome or Firefox recommended for best Web Audio API support

## Next Steps

After successful setup:

1. **Explore the Code**: Review the architecture in [README.md](./README.md)
2. **Run Tests**: Execute backend and frontend test suites  
3. **Make Changes**: Follow the contributing guidelines in the README
4. **Deploy**: Use GitHub Actions for automatic deployment to Azure

For questions or issues, please open an issue in the GitHub repository.