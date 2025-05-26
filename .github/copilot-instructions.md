# Contoso Voice Agent - Project Context

## Project Overview

The Contoso Voice Agent is a sophisticated full-stack AI-powered application that combines text chat and voice calling capabilities to provide personalized product recommendations and customer support. The system serves as a retail assistant for Contoso Outdoor Company, helping customers discover and purchase outdoor gear through natural conversations.

## Architecture

### High-Level System Design
```
┌─────────────────┐    WebSocket/HTTP    ┌──────────────────┐
│   Next.js       │◄────────────────────►│   FastAPI        │
│   Frontend      │                      │   Backend        │
│   (Port 3000)   │                      │   (Port 8000)    │
│                 │                      │                  │
│ ┌─────────────┐ │   Real-time Audio    │                  │
│ │ Web Audio   │ │──────────────────────┤                  │
│ │ Capture &   │ │      (WebSocket)     │                  │
│ │ Processing  │ │                      │                  │
│ └─────────────┘ │                      │                  │
└─────────────────┘                      └──────────────────┘
                                                   │
                                                   │ Audio Stream
                                                   ▼
                                         ┌──────────────────┐
                                         │   Azure OpenAI   │
                                         │   GPT-4o         │
                                         │   Realtime API   │
                                         └──────────────────┘
```

### Technology Stack

**Backend (Python FastAPI)**
- **Framework**: FastAPI with WebSocket support
- **AI Integration**: Azure OpenAI GPT-4o and Realtime API
- **Prompt Management**: Prompty framework for structured prompts
- **Session Management**: Custom session handling with conversation context
- **Data Models**: Pydantic models for type safety
- **Testing**: Pytest with evaluation framework

**Frontend (Next.js TypeScript)**
- **Framework**: Next.js 14 with App Router
- **State Management**: Zustand for global state
- **Audio Processing**: Web Audio API with custom worklets
- **Real-time Communication**: WebSocket client for voice/chat
- **UI Components**: React components with TypeScript
- **Styling**: CSS modules and styled components

**AI & Data**
- **Language Model**: Azure OpenAI GPT-4o for chat and suggestions
- **Voice Processing**: Azure OpenAI Realtime API for voice conversations
- **Product Data**: JSON-based product catalog (20 outdoor products)
- **User Data**: Purchase history and preferences in JSON format
- **Prompt Engineering**: Structured prompty files for different scenarios

## Core Features

### 1. Text Chat Interface
- **Location**: `web/src/components/chat/` and `api/chat/`
- **Functionality**: Real-time text conversations with AI assistant
- **AI Integration**: Uses `chat.prompty` with product catalog integration
- **State Management**: Zustand store (`web/src/store/chat.ts`)
- **WebSocket**: Real-time message exchange via WebSocket connection

### 2. Voice Calling System
- **Location**: `web/src/components/voice/` and `api/voice/`
- **Functionality**: Real-time voice conversations with AI
- **Audio Processing**: Custom Web Audio worklets for real-time audio
- **Voice Generation**: Azure OpenAI Realtime API integration
- **State Management**: Voice-specific Zustand store (`web/src/store/voice.ts`)

### 3. Product Recommendation Engine
- **Location**: `api/suggestions/` and integrated throughout
- **Functionality**: AI-powered product suggestions based on context
- **Data Sources**: Product catalog, purchase history, conversation context
- **Prompts**: `suggestions.prompty` for generating recommendations
- **Integration**: Embedded in both chat and voice interactions

### 4. Session Management
- **Location**: `api/session.py`
- **Functionality**: Maintains conversation context and user state
- **Features**: Message history, user preferences, conversation continuity
- **Storage**: In-memory session storage with conversation persistence

## Project Structure Deep Dive

### Backend API (`/api`)

#### Core Files
- **`main.py`**: FastAPI application entry point with WebSocket endpoints
- **`models.py`**: Pydantic data models for products, messages, sessions
- **`session.py`**: Session management and conversation context
- **`requirements.txt`**: Python dependencies (FastAPI, Azure OpenAI, etc.)

#### Chat Module (`/api/chat`)
- **`chat.prompty`**: Main chat prompt template with system instructions
- **`products.json`**: Product catalog for recommendations
- **`purchases.json`**: User purchase history data
- **`schema.json`**: JSON schema definitions

#### Suggestions Module (`/api/suggestions`)
- **`suggestions.prompty`**: Product suggestion prompt template
- **`writeup.prompty`**: Product writeup generation prompt
- **Supporting JSON files**: Products, purchases, and messages data

#### Voice Module (`/api/voice`)
- **`script.jinja2`**: Voice script template for AI responses

#### Testing (`/api/tests`)
- **`test_chat.py`**: Chat functionality tests
- **`test_suggestions.py`**: Recommendation engine tests
- **`evaluations.md`**: Testing methodology and results

### Frontend Web (`/web`)

#### App Structure (`/src/app`)
- **Next.js App Router**: Modern routing with layouts and pages
- **Main Pages**: Home, chat interface, voice interface
- **API Routes**: Integration endpoints for backend communication

#### Components (`/src/components`)
- **Chat Components**: Message display, input handling, conversation UI
- **Voice Components**: Call interface, audio controls, real-time indicators
- **Shared Components**: Common UI elements and layouts

#### Audio System (`/src/audio`)
- **Audio Processing**: Web Audio API integration
- **Worklets**: Custom audio processors for real-time voice
- **Recording**: Microphone capture and audio streaming

#### State Management (`/src/store`)
- **`chat.ts`**: Chat state, messages, and conversation management
- **`voice.ts`**: Voice call state, audio controls, call status
- **Zustand**: Lightweight state management with TypeScript support

#### Socket Integration (`/src/socket`)
- **WebSocket Client**: Real-time communication with backend
- **Event Handling**: Message routing and connection management

### Data Layer

#### Product Catalog
- **20 Outdoor Products**: Tents, backpacks, clothing, accessories
- **Rich Metadata**: Prices, descriptions, categories, brands, features
- **Image Assets**: Product photography in `/web/public/images`
- **Product Manuals**: Detailed specifications in `/web/public/manuals`

#### User Data
- **Purchase History**: Previous orders and preferences
- **Session Context**: Conversation history and user state
- **Recommendations**: AI-generated product suggestions

## Key Implementation Details

### AI Integration Patterns

#### Prompty Framework Usage
```markdown
# Example from chat.prompty
---
name: Chat
description: A chat function for the Contoso Outdoor Company assistant
authors:
  - Contoso
model:
  api: chat
  configuration:
    type: azure_openai
    azure_deployment: gpt-4o
    api_version: 2024-05-01-preview
  parameters:
    max_tokens: 1500
    temperature: 0.7
---
```

#### Session Management Pattern
```python
class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []
        self.context = {}
    
    def add_message(self, message: dict):
        self.messages.append(message)
        # Context management logic
```

### WebSocket Communication
- **Real-time Chat**: Bidirectional message exchange
- **Voice Streaming**: Audio data transmission
- **Session Sync**: State synchronization between client and server

### Audio Processing Architecture
- **Capture**: Microphone input via getUserMedia
- **Processing**: Custom AudioWorklet processors
- **Streaming**: Real-time audio transmission to Azure OpenAI
- **Playback**: AI-generated voice responses

## Development Workflows

### Local Development Setup
1. **Backend**: `cd api && pip install -r requirements.txt && python main.py`
2. **Frontend**: `cd web && npm install && npm run dev`
3. **Environment**: Configure Azure OpenAI credentials
4. **Testing**: Run pytest for backend, npm test for frontend

### AI Model Integration
- **Azure OpenAI**: GPT-4o for chat and recommendations
- **Realtime API**: Voice conversation capabilities
- **Prompt Engineering**: Structured prompts with context injection
- **Response Processing**: Typed response handling with Pydantic

### Data Flow Patterns
1. **User Input** → Frontend Component
2. **State Update** → Zustand Store
3. **WebSocket Send** → Backend API
4. **AI Processing** → Azure OpenAI
5. **Response** → Frontend Update
6. **UI Render** → User Interface

## Testing Strategy

### Backend Testing
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **AI Evaluation**: Prompt effectiveness testing
- **Performance Tests**: Response time and throughput

### Frontend Testing
- **Component Tests**: React component testing
- **Integration Tests**: WebSocket communication
- **Audio Tests**: Web Audio API functionality
- **E2E Tests**: Complete user workflows

## Deployment Considerations

### Container Support
- **Backend Dockerfile**: Python FastAPI containerization
- **Frontend Dockerfile**: Next.js application containerization
- **Multi-stage Builds**: Optimized production images

### Environment Configuration
- **Azure OpenAI**: API keys and endpoints
- **WebSocket**: Connection configuration
- **CORS**: Cross-origin resource sharing setup
- **Audio Permissions**: Microphone access requirements

## Extension Points

### Adding New Features
1. **New AI Capabilities**: Extend prompty templates
2. **Product Categories**: Expand product catalog
3. **User Personalization**: Enhanced recommendation algorithms
4. **Voice Features**: Additional voice processing capabilities

### Integration Opportunities
- **CRM Systems**: Customer data integration
- **E-commerce Platforms**: Order processing
- **Analytics**: Conversation and performance tracking
- **Mobile Apps**: Native mobile client development

## Troubleshooting Common Issues

### Audio Problems
- **Microphone Permissions**: Browser permission requirements
- **WebSocket Connection**: Network connectivity issues
- **Audio Worklets**: Browser compatibility considerations

### AI Integration Issues
- **API Limits**: Azure OpenAI rate limiting
- **Prompt Performance**: Response quality optimization
- **Context Management**: Conversation context handling

### Development Issues
- **CORS Configuration**: Cross-origin request setup
- **Environment Variables**: Azure credential management
- **Package Dependencies**: Version compatibility

This documentation provides a comprehensive understanding of the Contoso Voice Agent project, enabling AI assistants and developers to effectively navigate, understand, and contribute to the codebase.
