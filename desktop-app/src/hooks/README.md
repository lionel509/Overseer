# Custom React Hooks

## Overview

The hooks directory contains custom React hooks that provide reusable stateful logic for the Overseer desktop application. These hooks encapsulate complex functionality, API interactions, and state management patterns to promote code reuse and maintainability.

## Hook Categories

### 1. API Hooks (`/api/`)

#### useApi
- **Purpose**: Generic API request handling with loading states
- **Features**: Request/response handling, error management, caching
- **Usage**: Base hook for all API communications
- **TypeScript**: Full type safety with generic interfaces

#### useWebSocket
- **Purpose**: WebSocket connection management
- **Features**: Auto-reconnection, message queuing, connection status
- **Real-time**: Live updates from backend services
- **Error Handling**: Connection failures and recovery

#### useAuth
- **Purpose**: Authentication state and token management
- **Features**: Login/logout, token refresh, session persistence
- **Security**: Secure token storage and validation
- **Integration**: Works with backend authentication service

### 2. System Hooks (`/system/`)

#### useSystemMetrics
- **Purpose**: Real-time system performance monitoring
- **Features**: CPU, memory, disk usage tracking
- **Updates**: Live metric updates via WebSocket
- **Alerts**: Performance threshold notifications

#### useTaskManager
- **Purpose**: Task creation, monitoring, and management
- **Features**: Task lifecycle, scheduling, execution status
- **State**: Real-time task state synchronization
- **History**: Task execution history and logs

#### useNotifications
- **Purpose**: System notification management
- **Features**: Toast notifications, system alerts, badges
- **Persistence**: Notification history and preferences
- **Accessibility**: Screen reader compatible notifications

### 3. UI Hooks (`/ui/`)

#### useTheme
- **Purpose**: Theme management and switching
- **Features**: Dark/light mode, system preference detection
- **Persistence**: Theme preference storage
- **Animation**: Smooth theme transitions

#### useModal
- **Purpose**: Modal dialog state management
- **Features**: Stack management, focus handling, escape key
- **Accessibility**: Focus trapping and ARIA attributes
- **Animation**: Enter/exit transitions

#### useLocalStorage
- **Purpose**: Local storage with React state synchronization
- **Features**: Type-safe storage, change detection, SSR support
- **Persistence**: Automatic state persistence
- **Validation**: Data validation and migration

### 4. Data Hooks (`/data/`)

#### useCache
- **Purpose**: Client-side data caching and invalidation
- **Features**: TTL-based expiration, cache invalidation
- **Performance**: Optimized data retrieval
- **Memory**: Efficient memory management

#### useSearch
- **Purpose**: Search functionality with debouncing
- **Features**: Real-time search, result filtering, history
- **Performance**: Debounced input, result caching
- **UX**: Search suggestions and autocomplete

#### useForm
- **Purpose**: Form state management and validation
- **Features**: Field validation, error handling, submission
- **UX**: Real-time validation feedback
- **Accessibility**: Error message association

## Implementation Examples

### API Hook Example
```typescript
import { useState, useEffect } from 'react';

interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(url: string): ApiResponse<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(url);
      if (!response.ok) throw new Error('Request failed');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [url]);

  return { data, loading, error, refetch: fetchData };
}
```

### WebSocket Hook Example
```typescript
import { useState, useEffect, useRef } from 'react';

interface WebSocketHook {
  socket: WebSocket | null;
  connected: boolean;
  send: (message: string) => void;
  lastMessage: string | null;
}

export function useWebSocket(url: string): WebSocketHook {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = () => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setConnected(true);
      setSocket(ws);
    };
    
    ws.onmessage = (event) => {
      setLastMessage(event.data);
    };
    
    ws.onclose = () => {
      setConnected(false);
      setSocket(null);
      // Auto-reconnect after delay
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };
    
    ws.onerror = () => {
      setConnected(false);
    };
  };

  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socket) {
        socket.close();
      }
    };
  }, [url]);

  const send = (message: string) => {
    if (socket && connected) {
      socket.send(message);
    }
  };

  return { socket, connected, send, lastMessage };
}
```

### System Metrics Hook
```typescript
import { useState, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';

interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: { in: number; out: number };
  timestamp: number;
}

export function useSystemMetrics() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const { lastMessage } = useWebSocket('ws://localhost:8000/ws/metrics');

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        if (data.type === 'metrics') {
          setMetrics(data.payload);
        }
      } catch (error) {
        console.error('Failed to parse metrics:', error);
      }
    }
  }, [lastMessage]);

  return metrics;
}
```

## Hook Development Standards

### TypeScript Integration
- **Type Safety**: All hooks use TypeScript interfaces
- **Generic Types**: Support for flexible data types
- **Error Handling**: Proper error type definitions
- **Return Types**: Clear return type specifications

### State Management
- **Local State**: useState for hook-specific state
- **Effect Dependencies**: Proper dependency arrays
- **Cleanup**: useEffect cleanup functions
- **Memory Leaks**: Prevention of memory leaks

### Performance Optimization
- **Memoization**: useMemo and useCallback where appropriate
- **Debouncing**: Input debouncing for search and API calls
- **Caching**: Efficient data caching strategies
- **Lazy Loading**: Deferred loading of heavy resources

### Error Handling
- **Try-Catch**: Proper error catching and handling
- **Error States**: Clear error state management
- **User Feedback**: Meaningful error messages
- **Recovery**: Error recovery mechanisms

## Testing Strategy

### Unit Testing
```typescript
import { renderHook, act } from '@testing-library/react';
import { useApi } from './useApi';

describe('useApi', () => {
  it('should fetch data successfully', async () => {
    const { result } = renderHook(() => useApi('/api/test'));
    
    expect(result.current.loading).toBe(true);
    
    await act(async () => {
      // Wait for async operation
    });
    
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeDefined();
  });
});
```

### Integration Testing
- **Component Integration**: Test hooks within components
- **API Integration**: Test with real API endpoints
- **WebSocket Testing**: Test real-time functionality
- **State Synchronization**: Test state updates

### Mock Testing
- **API Mocking**: Mock external API calls
- **WebSocket Mocking**: Mock WebSocket connections
- **Timer Mocking**: Mock timers for debouncing
- **Storage Mocking**: Mock localStorage/sessionStorage

## Best Practices

### Hook Design
- **Single Responsibility**: Each hook has one clear purpose
- **Composition**: Hooks can be composed together
- **Reusability**: Designed for reuse across components
- **Flexibility**: Configurable through parameters

### State Management
- **Immutability**: State updates are immutable
- **Optimization**: Prevent unnecessary re-renders
- **Synchronization**: Keep state synchronized
- **Persistence**: Handle state persistence when needed

### Error Handling
- **Graceful Degradation**: Handle errors gracefully
- **User Experience**: Provide meaningful feedback
- **Logging**: Log errors for debugging
- **Recovery**: Implement recovery mechanisms

## Integration Points

### Redux Integration
- **Store Connection**: Access Redux store in hooks
- **Action Dispatch**: Dispatch actions from hooks
- **State Selection**: Select state slices efficiently
- **Middleware**: Work with Redux middleware

### Component Integration
- **Props**: Pass hook data as props
- **Context**: Use React Context for data sharing
- **Effects**: Trigger effects from hook changes
- **Callbacks**: Handle component callbacks

### External Services
- **API Services**: Integrate with backend APIs
- **WebSocket Services**: Real-time communication
- **Storage Services**: Data persistence
- **Authentication**: User authentication state

## Future Enhancements

### Advanced Features
- **Suspense**: React Suspense integration
- **Concurrent Mode**: Concurrent rendering support
- **Server State**: Server state management
- **Offline Support**: Offline functionality

### Performance
- **Virtualization**: Large list handling
- **Streaming**: Data streaming support
- **Batching**: Batch multiple operations
- **Prefetching**: Predictive data loading

### Developer Experience
- **DevTools**: Custom hook debugging
- **Hot Reload**: Hook hot reloading
- **Documentation**: Interactive hook documentation
- **Testing**: Enhanced testing utilities

This custom hooks system provides a solid foundation for managing complex stateful logic in the Overseer desktop application, promoting code reuse and maintainability while ensuring type safety and performance.
