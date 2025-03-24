# Realtime Chat API

A FastAPI-based realtime chat API with voice capabilities.

## Features

- Real-time chat functionality with websocket support
- Voice chat capabilities with Azure integration
- Suggestion generation
- Session management
- Telemetry and tracing

## Quick Start

1. Setup your Python environment (3.8+ required):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install the package with development dependencies:
```bash
make install
```

3. Create a `.env` file with required settings:
```
AZURE_VOICE_ENDPOINT=your_endpoint_here
AZURE_VOICE_KEY=your_key_here
LOCAL_TRACING_ENABLED=true
```

4. Run tests to verify setup:
```bash
make test
```

5. Start the development server:
```bash
uvicorn realtime_chat.main:app --reload
```

## Development

- Format code: `make format`
- Run linters: `make lint`
- Run tests: `make test`
- Clean temp files: `make clean`

## Project Structure

```
realtime_chat/
├── core/            # Core functionality and models
├── handlers/        # Route handlers and websocket endpoints  
├── config/         # Configuration files and templates
├── tests/          # Test suite
├── chat/           # Chat-related files and prompts
├── suggestions/    # Suggestion generation
└── call/           # Call/voice related templates
```

## Contributing

1. Ensure all tests pass locally
2. Run formatters and linters before committing
3. Add tests for new functionality
4. Update documentation as needed

## License

[Insert License Information]