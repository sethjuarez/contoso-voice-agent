# Contoso Voice Agent Setup Guide

This document provides comprehensive instructions for setting up and running the Contoso Voice Agent project on your development environment.

## Project Summary

The Contoso Voice Agent is a sophisticated AI-powered application that combines text chat and voice calling capabilities to provide personalized product recommendations and customer support. It serves as a retail assistant for Contoso Outdoor Company, helping customers discover and purchase outdoor gear through natural conversations.

For a complete overview of the project's architecture, components, and features, please refer to the [README.md](README.md).

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python](https://www.python.org/downloads/) 3.10 or higher
- [Node.js](https://nodejs.org/) 18 or higher
- [npm](https://www.npmjs.com/) (comes with Node.js)
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) (optional, for containerized deployment)

## Setting Up the API Backend

The backend is built with Python using FastAPI and provides WebSocket endpoints for real-time communication with the frontend.

### 1. Clone the Repository

```bash
git clone https://github.com/sethjuarez/contoso-voice-agent.git
cd contoso-voice-agent
```

### 2. Configure Environment Variables

Create a `.env` file in the `api` directory with the following variables:

```bash
cd api
touch .env
```

Add the following environment variables to the `.env` file:

```
AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_VOICE_ENDPOINT=your-azure-voice-endpoint
AZURE_VOICE_KEY=your-azure-voice-key
LOCAL_TRACING_ENABLED=true
```

Replace the placeholder values with your actual Azure OpenAI credentials.

### 3. Create a Python Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the API Server

```bash
python main.py
```

The API server will start running on http://localhost:8000.

## Setting Up the Web Frontend

The frontend is built with Next.js and TypeScript, providing a responsive user interface for interacting with the AI assistant.

### 1. Navigate to the Web Directory

```bash
cd ../web  # From the api directory
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start the Development Server

```bash
npm run dev
```

The frontend development server will start running on http://localhost:3000.

## Running Everything Together

To run both the backend and frontend simultaneously:

### Option 1: Using Separate Terminals

1. In the first terminal:
   ```bash
   cd api
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   ```

2. In the second terminal:
   ```bash
   cd web
   npm run dev
   ```

### Option 2: Using VS Code

The project includes VS Code launch configurations for debugging both frontend and backend components simultaneously.

1. Open the project in VS Code:
   ```bash
   code .
   ```

2. Press `F5` to start debugging both components.

### Option 3: Using Docker Compose (Development)

1. Create a `docker-compose.yml` file in the root directory:

```yaml
version: '3'
services:
  api:
    build:
      context: ./api
    ports:
      - "8000:8000"
    env_file:
      - ./api/.env
    volumes:
      - ./api:/api

  web:
    build:
      context: ./web
    ports:
      - "3000:3000"
    depends_on:
      - api
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. Run Docker Compose:

```bash
docker-compose up
```

## GitHub Actions for Deployment

The project includes GitHub Actions workflows for deploying both the frontend and backend to Azure Container Apps.

### Workflow Overview

1. **Backend Deployment (`azure-container-api.yml`)**: Builds and deploys the FastAPI backend to Azure Container Apps.
2. **Frontend Deployment (`azure-container-web.yml`)**: Builds and deploys the Next.js frontend to Azure Container Apps.

### How the Deployment Works

The deployment process follows these steps:

1. **Trigger**: Workflows are triggered on pushes to the `main` branch or manually via workflow dispatch.
   - Backend workflow is triggered when changes are made to files in the `api` directory.
   - Frontend workflow is triggered when changes are made to files in the `web` directory.

2. **Build Process**:
   - Creates a version tag based on the current date and time
   - Logs in to Azure using service principal credentials
   - Builds a Docker image from the Dockerfile in each component's directory
   - Pushes the Docker image to the configured Azure Container Registry

3. **Deployment Process**:
   - Uses `az containerapp up` command to deploy the containerized application
   - Configures ingress, target ports, and environment variables
   - For the web app, sets up autoscaling rules

### Required Secrets

The GitHub Actions workflows require the following secrets to be configured in the repository:

- `AZURE_CLIENT_ID`: The client ID for Azure service principal
- `AZURE_TENANT_ID`: The tenant ID for Azure service principal
- `AZURE_SUBSCRIPTION_ID`: The Azure subscription ID
- `REGISTRY_ENDPOINT`: The Azure Container Registry endpoint
- `REGISTRY_USERNAME`: The username for the Azure Container Registry
- `REGISTRY_PASSWORD`: The password for the Azure Container Registry

Additionally, the following secrets are referenced in the Container App environment:
- `azure-openai-endpoint`: Azure OpenAI endpoint
- `azure-openai-api-key`: Azure OpenAI API key
- `azure-voice-endpoint`: Azure Voice endpoint
- `azure-voice-key`: Azure Voice key
- `appinsights-connectionstring`: Application Insights connection string

### Setting Up GitHub Actions (For Contributors)

To use these workflows in your fork:

1. Fork the repository
2. Set up the required secrets in your forked repository's Settings > Secrets and variables > Actions
3. Create an Azure Container Registry and Container Apps environment
4. Update the resource group and environment names in the workflow files if needed

## Troubleshooting

### Common Issues

1. **Connection refused when connecting to backend**
   
   Ensure that the backend server is running and listening on port 8000. Check for any error messages in the terminal where the backend is running.

2. **CORS errors in the browser console**
   
   The backend is configured to accept connections from the frontend running on localhost:3000. If you're running the frontend on a different port, you may need to update the CORS configuration in the backend.

3. **Azure OpenAI authentication errors**
   
   Verify that your Azure OpenAI credentials are correctly configured in the `.env` file. Ensure that your Azure subscription has access to the required OpenAI models.

### Getting Help

If you encounter any issues not covered here, please open an issue on the [GitHub repository](https://github.com/sethjuarez/contoso-voice-agent/issues).