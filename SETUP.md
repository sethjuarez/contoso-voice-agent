# Contoso Voice Agent Setup Guide

This document provides comprehensive instructions for setting up and running the Contoso Voice Agent project on your development machine.

## Project Overview

The Contoso Voice Agent is a sophisticated AI-powered voice and text assistant for Contoso Outdoors that provides personalized product recommendations and customer support through natural conversations. 

For more detailed information about the project, please refer to the [README.md](README.md).

## Prerequisites

Before setting up the project, ensure you have the following installed:

- [Python](https://www.python.org/downloads/) 3.9 or later
- [Node.js](https://nodejs.org/) 18 or later
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- [Docker](https://www.docker.com/) (optional, for container-based development and deployment)
- [Git](https://git-scm.com/)

## Backend Setup (API)

The backend is a Python FastAPI application that handles WebSocket connections and integrates with Azure OpenAI services.

### Clone the Repository

```bash
git clone https://github.com/sethjuarez/contoso-voice-agent.git
cd contoso-voice-agent
```

### Setting Up Environment Variables

Create a `.env` file in the `api` directory with the following variables:

```bash
cd api
touch .env
```

Add the following environment variables to the `.env` file:

```
AZURE_VOICE_ENDPOINT=your_azure_voice_endpoint
AZURE_VOICE_KEY=your_azure_voice_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
LOCAL_TRACING_ENABLED=true
```

Replace the placeholders with your actual Azure OpenAI service credentials.

### Installing Dependencies

```bash
cd api  # If not already in the api directory
pip install -r requirements.txt
```

### Running the Backend Locally

```bash
python main.py
```

The API will be accessible at `http://localhost:8000`.

## Frontend Setup (Web)

The frontend is a Next.js application that provides the user interface for both text chat and voice capabilities.

### Installing Dependencies

```bash
cd web
npm install
```

Or if you prefer yarn:

```bash
cd web
yarn install
```

### Running the Frontend Locally

```bash
npm run dev
```

Or with yarn:

```bash
yarn dev
```

The frontend will be accessible at `http://localhost:3000`.

## Running Both Components Together

To run both the frontend and backend applications simultaneously:

### Using VS Code

The project includes VS Code launch configurations. If you're using VS Code:

1. Open the project in VS Code
2. Press `F5` to start debugging both frontend and backend components simultaneously

### Using Command Line

1. Open two separate terminal windows
2. In the first terminal:
   ```bash
   cd api
   python main.py
   ```
3. In the second terminal:
   ```bash
   cd web
   npm run dev
   ```

## Verifying the Setup

Once both services are running:

1. Navigate to `http://localhost:3000` in your browser
2. You should see the Contoso Voice Agent web interface
3. The frontend should be able to connect to the backend through WebSocket and HTTP APIs

## Deployment with GitHub Actions

The project includes GitHub Actions workflows that automate the deployment to Azure Container Apps.

### Deployment Workflows

1. **API Deployment** (`.github/workflows/azure-container-api.yml`):
   - Triggered when changes are pushed to the `main` branch in the `api/` directory
   - Builds and deploys the API container to Azure Container Apps
   - Sets environment variables including Azure OpenAI credentials

2. **Web Deployment** (`.github/workflows/azure-container-web.yml`):
   - Triggered when changes are pushed to the `main` branch in the `web/` directory
   - Configures endpoints to connect to the deployed API
   - Builds and deploys the web container to Azure Container Apps

### Required Secrets for GitHub Actions

To use the deployment workflows, the following secrets must be configured in the GitHub repository:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `REGISTRY_ENDPOINT`
- `REGISTRY_USERNAME`
- `REGISTRY_PASSWORD`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_VOICE_ENDPOINT`
- `AZURE_VOICE_KEY`
- `APPINSIGHTS_CONNECTIONSTRING`

### Manual Deployment

To manually trigger a deployment:

1. Navigate to the Actions tab in the GitHub repository
2. Select either the "Build and deploy contoso-voice-api" or "Build and deploy contoso-voice-web" workflow
3. Click "Run workflow" and select the branch to deploy from

## Troubleshooting

### Common Issues

1. **Connection Error**: If the frontend cannot connect to the backend, check that:
   - The backend is running on port 8000
   - The endpoint.ts file has the correct WebSocket and API endpoints

2. **Missing Environment Variables**: If the backend fails to start, check your `.env` file has all required environment variables

3. **Azure OpenAI Integration**: If AI features aren't working, verify your Azure OpenAI credentials are correct and the service is properly configured

### Getting Help

If you encounter issues not covered here, please open an issue in the GitHub repository with details about the problem and steps to reproduce it.