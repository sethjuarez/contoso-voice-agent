# Recommendations for Improving Testability

## Introduction

This document outlines recommendations for making the Contoso Voice Agent backend more testable. These recommendations focus on architectural changes that would make the code easier to test without changing core functionality.

## Key Recommendations

### 1. Dependency Injection

**Current Issue**: Many modules have direct dependencies on external services and resources (like OpenAI client, file access, etc.), making them difficult to mock.

**Recommendation**: Implement dependency injection by:

- Creating service interfaces that can be implemented by both real and mock versions
- Using function parameters to pass dependencies instead of creating them within functions
- Creating factory functions that can be easily mocked in tests

**Example Change**:

```python
# Before
def some_function():
    client = AsyncAzureOpenAI(
        azure_endpoint=AZURE_VOICE_ENDPOINT,
        api_key=AZURE_VOICE_KEY,
        api_version="2024-10-01-preview",
    )
    # ... use client

# After
def some_function(client=None):
    if client is None:
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_VOICE_ENDPOINT,
            api_key=AZURE_VOICE_KEY,
            api_version="2024-10-01-preview",
        )
    # ... use client
```

### 2. Data Source Abstraction

**Current Issue**: Direct file access for products and purchases makes it difficult to test with different data.

**Recommendation**: Abstract data access through a data provider:

- Create a data provider interface with methods like `get_products()` and `get_purchases()`
- Implement concrete providers: `FileDataProvider`, `MockDataProvider`, etc.
- Use the provider in all code that needs access to data

**Example Change**:

```python
# Define an interface
class DataProvider:
    def get_products(self):
        pass
    
    def get_purchases(self):
        pass

# Implement a concrete file-based provider
class FileDataProvider(DataProvider):
    def __init__(self, base_path):
        self.base_path = base_path
        
    def get_products(self):
        return json.loads((self.base_path / "products.json").read_text())
        
    def get_purchases(self):
        return json.loads((self.base_path / "purchases.json").read_text())

# Use in application
data_provider = FileDataProvider(base_path)
products = data_provider.get_products()
purchases = data_provider.get_purchases()
```

### 3. Configuration Management

**Current Issue**: Settings are scattered throughout the code, making it difficult to configure the application for testing.

**Recommendation**: Centralize configuration:

- Create a `Config` class that holds all application settings
- Load configuration from environment variables, files, or defaults
- Pass Config instances to other components that need configuration

**Example Change**:

```python
class Config:
    def __init__(self):
        self.azure_voice_endpoint = os.getenv("AZURE_VOICE_ENDPOINT", "fake_endpoint")
        self.azure_voice_key = os.getenv("AZURE_VOICE_KEY", "fake_key")
        self.local_tracing_enabled = os.getenv("LOCAL_TRACING_ENABLED", "true") == "true"
        # Add more settings as needed

# Use in the application
config = Config()
init_tracing(local_tracing=config.local_tracing_enabled)
```

### 4. WebSocket Abstraction

**Current Issue**: Direct use of WebSocket makes testing endpoints difficult.

**Recommendation**: Abstract WebSocket interactions:

- Create a `WebSocketHandler` class that wraps WebSocket operations
- Use the handler in endpoints instead of using WebSocket directly
- Implement a mock handler for testing

**Example Change**:

```python
class WebSocketHandler:
    def __init__(self, websocket):
        self.websocket = websocket
        
    async def accept(self):
        await self.websocket.accept()
        
    async def receive_json(self):
        return await self.websocket.receive_json()
        
    async def send_json(self, data):
        await self.websocket.send_json(data)
        
    async def close(self):
        await self.websocket.close()

# Use in endpoint
async def chat_endpoint(websocket: WebSocket):
    ws_handler = WebSocketHandler(websocket)
    await ws_handler.accept()
    # Use ws_handler instead of websocket directly
```

### 5. Service Classes

**Current Issue**: Complex endpoint functions with multiple responsibilities.

**Recommendation**: Extract functionality into service classes:

- Create service classes for distinct areas of functionality (ChatService, VoiceService, etc.)
- Move logic from endpoints to these services
- Make endpoints thin wrappers around service calls

**Example Change**:

```python
class ChatService:
    def __init__(self, session_manager, data_provider):
        self.session_manager = session_manager
        self.data_provider = data_provider
        
    async def handle_chat_message(self, thread_id, websocket):
        # Logic moved from chat_endpoint
        pass

# Use in endpoint
@app.websocket("/api/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        thread_id = data["threadId"]
        await chat_service.handle_chat_message(thread_id, websocket)
    except WebSocketDisconnect:
        print("Chat Socket Disconnected")
```

## Implementation Strategy

1. **Start Small**: Begin with simple refactorings that have the highest impact on testability
2. **Incremental Changes**: Make changes incrementally, ensuring tests pass after each change
3. **Progressive Abstraction**: Start with basic dependency injection, then move to more complex abstractions
4. **Focus on Seams**: Identify "seams" in the code where abstractions can be introduced with minimal disruption
5. **Top-Down Approach**: Start with high-level abstractions and then refine lower-level details

## Benefits

- **Enhanced Testability**: More direct control over dependencies during tests
- **Improved Maintainability**: Clearer separation of concerns
- **Better Extensibility**: Easier to add new features or change implementations
- **Reduced Test Complexity**: Simpler mocking requirements for tests
- **Improved Test Coverage**: More components can be tested in isolation