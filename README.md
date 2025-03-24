# Voice + Text Configurator

A real-time voice and text configuration system that enables interactive communication between users and an AI assistant. The system supports both text chat and voice interactions with automatic speech recognition and text-to-speech capabilities.

## Project Structure

- `/api` - FastAPI backend server
  - Real-time voice processing
  - WebSocket communication
  - Chat message handling
  - AI suggestion generation
- `/web` - TypeScript/React frontend
  - Audio recording and playback
  - WebSocket client implementation
  - User interface components
  - State management

## Setup

1. Install dependencies:
   ```bash
   # Backend
   cd api
   pip install -r requirements.txt

   # Frontend
   cd web
   npm install
   ```

2. Configure environment variables:
   ```
   AZURE_VOICE_ENDPOINT=<your-azure-voice-endpoint>
   AZURE_VOICE_KEY=<your-azure-voice-key>
   LOCAL_TRACING_ENABLED=true  # Optional, for local development
   ```

## Key Features

- Real-time voice communication with AI assistant
- Automatic speech recognition
- Text-to-speech output
- WebSocket-based bidirectional communication
- Context-aware responses using chat history
- Configurable voice settings (threshold, silence duration, etc.)
- Support for multiple audio devices

## Usage

1. Start the API server:
   ```bash
   cd api
   uvicorn main:app --reload
   ```

2. Start the web client:
   ```bash
   cd web
   npm start
   ```

3. Access the application at http://localhost:3000

## WebSocket Protocol

The system uses two WebSocket endpoints:

- `/api/chat` - Text-based chat communication
- `/api/voice` - Voice communication with real-time audio streaming

Message types:
- `audio` - Raw audio data (base64 encoded)
- `text` - Text messages
- `interrupt` - Control messages
- `user` - User input
- `system` - System messages

## Architecture

```
[Web Client] <--WebSocket--> [FastAPI Server] <---> [Azure Voice Services]
    |                              |
    |                              |
 [Audio Processing]        [Session Management]
 [User Interface]          [Message Routing]
```

The system uses a real-time client for voice processing, with configurable parameters for voice activity detection and audio processing.
