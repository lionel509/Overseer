# Services Layer

## Overview

The services directory contains all service classes and modules that handle external communications, data processing, and business logic for the Overseer desktop application. These services provide a clean abstraction layer between the UI components and external resources.

## Service Architecture

### Service Categories

```
services/
├── api/              # HTTP API communication
├── websocket/        # Real-time WebSocket services
├── auth/            # Authentication and authorization
├── storage/         # Data storage and caching
├── system/          # System integration services
├── ai/              # AI model integration
├── utils/           # Utility services
└── types/           # Service type definitions
```

## Core Services

### 1. API Service (`/api/`)

#### ApiClient
- **Purpose**: Centralized HTTP client for backend communication
- **Features**: Request/response interceptors, error handling, retries
- **Configuration**: Base URL, headers, timeouts, authentication
- **TypeScript**: Full type safety for all API calls

#### EndpointService
- **Purpose**: Organized API endpoint management
- **Features**: RESTful operations, parameter validation
- **Endpoints**: System metrics, tasks, settings, user data
- **Caching**: Response caching and invalidation

#### ErrorHandler
- **Purpose**: Centralized error handling and user feedback
- **Features**: Error categorization, retry logic, notifications
- **UX**: User-friendly error messages and recovery options
- **Logging**: Comprehensive error logging and reporting

### 2. WebSocket Service (`/websocket/`)

#### WebSocketClient
- **Purpose**: Real-time communication with backend
- **Features**: Auto-reconnection, message queuing, event handling
- **Protocol**: JSON-based message protocol
- **State**: Connection state management and monitoring

#### EventDispatcher
- **Purpose**: WebSocket event routing and handling
- **Features**: Event subscription, message filtering, callbacks
- **Performance**: Efficient event processing and memory management
- **Integration**: Seamless integration with React components

#### RealtimeService
- **Purpose**: High-level real-time data synchronization
- **Features**: Live updates, conflict resolution, offline support
- **Data**: System metrics, task status, notifications
- **Optimization**: Bandwidth optimization and data compression

### 3. Authentication Service (`/auth/`)

#### AuthService
- **Purpose**: User authentication and session management
- **Features**: Login/logout, token refresh, session persistence
- **Security**: Secure token storage, encryption, validation
- **Integration**: Seamless integration with API services

#### TokenManager
- **Purpose**: JWT token management and validation
- **Features**: Token storage, expiration handling, refresh logic
- **Security**: Secure storage, automatic refresh, revocation
- **Performance**: Efficient token validation and caching

#### SecurityService
- **Purpose**: Security-related utilities and validation
- **Features**: Input validation, XSS protection, CSRF protection
- **Compliance**: Security best practices and standards
- **Auditing**: Security event logging and monitoring

### 4. Storage Service (`/storage/`)

#### LocalStorageService
- **Purpose**: Local data storage and retrieval
- **Features**: Type-safe storage, data validation, migration
- **Persistence**: User preferences, application state, cache
- **Encryption**: Sensitive data encryption and protection

#### CacheService
- **Purpose**: In-memory and persistent caching
- **Features**: TTL-based expiration, cache invalidation, statistics
- **Performance**: Fast data access, memory optimization
- **Storage**: Multi-level caching with fallback mechanisms

#### FileService
- **Purpose**: File system operations and management
- **Features**: File upload/download, directory management
- **Integration**: Electron file system integration
- **Security**: File access validation and sanitization

### 5. System Service (`/system/`)

#### SystemMonitor
- **Purpose**: System resource monitoring and reporting
- **Features**: CPU, memory, disk, network monitoring
- **Real-time**: Live metrics via WebSocket connection
- **Alerts**: Threshold-based alerts and notifications

#### TaskService
- **Purpose**: Task management and execution
- **Features**: Task creation, scheduling, monitoring, history
- **State**: Real-time task state synchronization
- **Integration**: Deep system integration for task execution

#### NotificationService
- **Purpose**: System notifications and alerts
- **Features**: Toast notifications, system tray, badges
- **Persistence**: Notification history and preferences
- **Accessibility**: Screen reader compatible notifications

### 6. AI Service (`/ai/`)

#### AIClient
- **Purpose**: AI model communication and management
- **Features**: Model loading, inference, response processing
- **Integration**: Gemma 3n model integration
- **Performance**: Efficient model usage and caching

#### ChatService
- **Purpose**: AI chat functionality and context management
- **Features**: Message history, context preservation, personalization
- **UX**: Natural conversation flow and response formatting
- **Learning**: Continuous learning from user interactions

#### VoiceService
- **Purpose**: Speech recognition and synthesis
- **Features**: Voice input/output, language support
- **Integration**: Web Speech API and native speech services
- **Accessibility**: Voice accessibility features

## Implementation Examples

### API Service Example
```typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios';

export class ApiClient {
  private client: AxiosInstance;
  
  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Handle token refresh
          await this.refreshToken();
          return this.client.request(error.config);
        }
        return Promise.reject(error);
      }
    );
  }
  
  async get<T>(url: string): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url);
    return response.data;
  }
  
  async post<T>(url: string, data: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data);
    return response.data;
  }
  
  private async refreshToken(): Promise<void> {
    // Token refresh logic
  }
}
```

### WebSocket Service Example
```typescript
export class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private eventHandlers: Map<string, Function[]> = new Map();
  
  connect(url: string): void {
    this.socket = new WebSocket(url);
    
    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect();
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  private handleMessage(message: any): void {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => handler(message.payload));
    }
  }
  
  on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }
  
  send(type: string, payload: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, payload }));
    }
  }
  
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        this.connect(this.socket!.url);
      }, 1000 * this.reconnectAttempts);
    }
  }
}
```

### System Monitor Example
```typescript
export class SystemMonitor {
  private webSocketService: WebSocketService;
  private metricsCallbacks: Function[] = [];
  
  constructor(webSocketService: WebSocketService) {
    this.webSocketService = webSocketService;
    this.setupListeners();
  }
  
  private setupListeners(): void {
    this.webSocketService.on('system_metrics', (metrics) => {
      this.metricsCallbacks.forEach(callback => callback(metrics));
    });
  }
  
  onMetricsUpdate(callback: (metrics: SystemMetrics) => void): void {
    this.metricsCallbacks.push(callback);
  }
  
  async getCurrentMetrics(): Promise<SystemMetrics> {
    // Fetch current metrics from API
    return await this.apiClient.get<SystemMetrics>('/api/system/metrics');
  }
  
  async getMetricsHistory(timeRange: string): Promise<SystemMetrics[]> {
    return await this.apiClient.get<SystemMetrics[]>(`/api/system/metrics/history?range=${timeRange}`);
  }
}
```

## Service Development Standards

### TypeScript Integration
- **Type Safety**: All services use TypeScript interfaces
- **Generic Types**: Support for flexible data types
- **Error Handling**: Proper error type definitions
- **API Contracts**: Clear interface definitions

### Error Handling
- **Consistent Errors**: Standardized error format
- **Error Recovery**: Automatic retry mechanisms
- **User Feedback**: Meaningful error messages
- **Logging**: Comprehensive error logging

### Performance Optimization
- **Caching**: Efficient data caching strategies
- **Debouncing**: Request debouncing for performance
- **Connection Pooling**: Efficient connection management
- **Memory Management**: Proper cleanup and disposal

### Testing Strategy
- **Unit Tests**: Individual service testing
- **Integration Tests**: Service integration testing
- **Mock Services**: Mock external dependencies
- **Performance Tests**: Load and stress testing

## Service Configuration

### Environment Configuration
```typescript
export const ServiceConfig = {
  api: {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    timeout: 10000,
    retryAttempts: 3,
  },
  websocket: {
    url: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
    reconnectAttempts: 5,
    heartbeatInterval: 30000,
  },
  auth: {
    tokenRefreshThreshold: 5 * 60 * 1000, // 5 minutes
    sessionTimeout: 24 * 60 * 60 * 1000, // 24 hours
  },
  cache: {
    defaultTTL: 5 * 60 * 1000, // 5 minutes
    maxSize: 100 * 1024 * 1024, // 100MB
  },
};
```

### Service Registry
```typescript
export class ServiceRegistry {
  private services: Map<string, any> = new Map();
  
  register<T>(name: string, service: T): void {
    this.services.set(name, service);
  }
  
  get<T>(name: string): T {
    return this.services.get(name) as T;
  }
  
  initialize(): void {
    // Initialize all services
    this.register('api', new ApiClient(ServiceConfig.api.baseURL));
    this.register('websocket', new WebSocketService());
    this.register('auth', new AuthService());
    this.register('storage', new LocalStorageService());
    this.register('system', new SystemMonitor(this.get('websocket')));
  }
}
```

## Integration Points

### Component Integration
- **Hooks**: Custom hooks for service access
- **Context**: React Context for service provision
- **State**: Integration with global state management
- **Effects**: Service integration with React lifecycle

### Backend Integration
- **API Endpoints**: RESTful API communication
- **WebSocket**: Real-time data synchronization
- **Authentication**: Secure service authentication
- **Error Handling**: Consistent error responses

### System Integration
- **Electron**: Native desktop integration
- **File System**: File operations and monitoring
- **OS Services**: Operating system integration
- **Hardware**: Hardware monitoring and control

## Security Considerations

### Data Protection
- **Encryption**: Sensitive data encryption
- **Validation**: Input validation and sanitization
- **Authentication**: Secure authentication mechanisms
- **Authorization**: Role-based access control

### Communication Security
- **HTTPS**: Secure HTTP communications
- **WSS**: Secure WebSocket connections
- **Token Security**: Secure token handling
- **Data Integrity**: Message integrity validation

## Future Enhancements

### Advanced Features
- **Service Mesh**: Distributed service architecture
- **Load Balancing**: Service load balancing
- **Circuit Breakers**: Fault tolerance patterns
- **Monitoring**: Service health monitoring

### Performance
- **Streaming**: Real-time data streaming
- **Compression**: Data compression algorithms
- **Caching**: Advanced caching strategies
- **Optimization**: Performance optimization techniques

This services layer provides a robust foundation for all external communications and business logic in the Overseer desktop application, ensuring clean separation of concerns and maintainable code architecture.
