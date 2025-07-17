# Utility Functions

## Overview

The utils directory contains reusable utility functions, helpers, and common logic used throughout the Overseer desktop application. These utilities promote code reuse, maintainability, and consistency across the application.

## Utility Categories

### Directory Structure

```
utils/
├── api/              # API-related utilities
├── data/             # Data processing utilities
├── date/             # Date and time utilities
├── format/           # Data formatting utilities
├── validation/       # Input validation utilities
├── storage/          # Local storage utilities
├── system/           # System-related utilities
├── constants/        # Application constants
├── types/            # Utility type definitions
└── index.ts          # Main utility exports
```

## Core Utilities

### 1. API Utilities (`/api/`)

#### Request Helpers
- **Purpose**: Common API request patterns and configurations
- **Features**: Request formatting, error handling, retry logic
- **Usage**: Standardize API communications across the app
- **TypeScript**: Full type safety for API calls

#### Response Processors
- **Purpose**: Standardize API response handling
- **Features**: Response transformation, error extraction
- **Integration**: Works with all API services
- **Validation**: Response validation and type checking

#### URL Builders
- **Purpose**: Dynamic URL construction for API endpoints
- **Features**: Parameter encoding, query string building
- **Security**: Input sanitization and validation
- **Flexibility**: Support for complex endpoint patterns

### 2. Data Utilities (`/data/`)

#### Array Helpers
- **Purpose**: Array manipulation and processing
- **Features**: Sorting, filtering, grouping, deduplication
- **Performance**: Optimized algorithms for large datasets
- **TypeScript**: Generic type support for type safety

#### Object Utilities
- **Purpose**: Object manipulation and transformation
- **Features**: Deep cloning, merging, property extraction
- **Immutability**: Immutable object operations
- **Validation**: Object structure validation

#### Collection Utilities
- **Purpose**: Data collection processing
- **Features**: Pagination, search, aggregation
- **Performance**: Efficient data processing
- **Flexibility**: Support for various data structures

### 3. Date/Time Utilities (`/date/`)

#### Date Formatting
- **Purpose**: Consistent date/time formatting
- **Features**: Multiple format options, localization
- **Timezone**: Timezone-aware formatting
- **Relative**: Relative time display (e.g., "2 hours ago")

#### Date Calculations
- **Purpose**: Date arithmetic and calculations
- **Features**: Add/subtract time, duration calculations
- **Business Logic**: Working days, business hours
- **Validation**: Date range validation

#### Time Zone Support
- **Purpose**: Multi-timezone support
- **Features**: Timezone conversion, detection
- **Localization**: Locale-specific formatting
- **Performance**: Efficient timezone handling

### 4. Validation Utilities (`/validation/`)

#### Input Validation
- **Purpose**: Form and user input validation
- **Features**: Email, URL, phone number validation
- **Security**: XSS prevention, input sanitization
- **Customization**: Custom validation rules

#### Schema Validation
- **Purpose**: Data structure validation
- **Features**: JSON schema validation, type checking
- **Integration**: Works with API responses
- **Error Handling**: Detailed validation errors

#### Security Validation
- **Purpose**: Security-focused validation
- **Features**: SQL injection prevention, file validation
- **Compliance**: Security best practices
- **Logging**: Security event logging

## Implementation Examples

### API Utilities Example
```typescript
// API request helper
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { method = 'GET', data, headers = {}, timeout = 10000 } = options;
  
  const config: RequestConfig = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    timeout,
  };
  
  if (data) {
    config.body = JSON.stringify(data);
  }
  
  try {
    const response = await fetch(endpoint, config);
    
    if (!response.ok) {
      throw new ApiError(response.status, response.statusText);
    }
    
    const result = await response.json();
    return { data: result, success: true };
  } catch (error) {
    return {
      data: null,
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// URL builder utility
export function buildUrl(
  baseUrl: string,
  path: string,
  params: Record<string, any> = {}
): string {
  const url = new URL(path, baseUrl);
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, String(value));
    }
  });
  
  return url.toString();
}

// Response processor
export function processApiResponse<T>(
  response: any,
  validator?: (data: any) => data is T
): T | null {
  if (!response || typeof response !== 'object') {
    return null;
  }
  
  if (validator && !validator(response)) {
    console.warn('API response validation failed', response);
    return null;
  }
  
  return response as T;
}
```

### Data Utilities Example
```typescript
// Array utilities
export function uniqueBy<T>(
  array: T[],
  keySelector: (item: T) => any
): T[] {
  const seen = new Set();
  return array.filter(item => {
    const key = keySelector(item);
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

export function groupBy<T, K extends string | number>(
  array: T[],
  keySelector: (item: T) => K
): Record<K, T[]> {
  return array.reduce((groups, item) => {
    const key = keySelector(item);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {} as Record<K, T[]>);
}

export function sortBy<T>(
  array: T[],
  keySelector: (item: T) => any,
  direction: 'asc' | 'desc' = 'asc'
): T[] {
  return [...array].sort((a, b) => {
    const aValue = keySelector(a);
    const bValue = keySelector(b);
    
    if (aValue < bValue) return direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return direction === 'asc' ? 1 : -1;
    return 0;
  });
}

// Object utilities
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as any;
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as any;
  }
  
  if (typeof obj === 'object') {
    const cloned = {} as any;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }
  
  return obj;
}

export function mergeDeep<T extends Record<string, any>>(
  target: T,
  source: Partial<T>
): T {
  const result = { ...target };
  
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      const sourceValue = source[key];
      const targetValue = result[key];
      
      if (
        typeof sourceValue === 'object' &&
        sourceValue !== null &&
        !Array.isArray(sourceValue) &&
        typeof targetValue === 'object' &&
        targetValue !== null &&
        !Array.isArray(targetValue)
      ) {
        result[key] = mergeDeep(targetValue, sourceValue);
      } else {
        result[key] = sourceValue as any;
      }
    }
  }
  
  return result;
}
```

### Date Utilities Example
```typescript
// Date formatting utilities
export function formatDate(
  date: Date | string,
  format: 'short' | 'medium' | 'long' | 'full' = 'medium'
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  const options: Intl.DateTimeFormatOptions = {
    short: { month: 'short', day: 'numeric' },
    medium: { month: 'short', day: 'numeric', year: 'numeric' },
    long: { month: 'long', day: 'numeric', year: 'numeric' },
    full: { 
      weekday: 'long', 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric' 
    },
  }[format];
  
  return dateObj.toLocaleDateString(undefined, options);
}

export function formatRelativeTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'just now';
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  }
  
  return formatDate(dateObj);
}

export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

export function isValidDate(date: any): date is Date {
  return date instanceof Date && !isNaN(date.getTime());
}
```

### Validation Utilities Example
```typescript
// Input validation
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .trim();
}

export function validateRequired(value: any): boolean {
  if (value === null || value === undefined) {
    return false;
  }
  
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  
  return true;
}

export function validateLength(
  value: string,
  min: number,
  max: number
): boolean {
  const length = value.length;
  return length >= min && length <= max;
}

// Schema validation
export function validateSchema<T>(
  data: any,
  schema: ValidationSchema<T>
): ValidationResult<T> {
  const errors: ValidationError[] = [];
  
  for (const [key, rules] of Object.entries(schema)) {
    const value = data[key];
    
    for (const rule of rules) {
      const result = rule.validate(value);
      if (!result.valid) {
        errors.push({
          field: key,
          message: result.message,
          code: rule.code,
        });
      }
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data as T : null,
  };
}
```

### Storage Utilities Example
```typescript
// Local storage utilities
export function getFromStorage<T>(
  key: string,
  defaultValue: T
): T {
  try {
    const item = localStorage.getItem(key);
    if (item === null) {
      return defaultValue;
    }
    return JSON.parse(item);
  } catch (error) {
    console.warn(`Failed to get item from storage: ${key}`, error);
    return defaultValue;
  }
}

export function setToStorage<T>(key: string, value: T): boolean {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.warn(`Failed to set item in storage: ${key}`, error);
    return false;
  }
}

export function removeFromStorage(key: string): boolean {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.warn(`Failed to remove item from storage: ${key}`, error);
    return false;
  }
}

export function clearStorage(): boolean {
  try {
    localStorage.clear();
    return true;
  } catch (error) {
    console.warn('Failed to clear storage', error);
    return false;
  }
}

// Storage with expiration
export function setWithExpiration<T>(
  key: string,
  value: T,
  expirationMinutes: number
): boolean {
  const expirationTime = new Date().getTime() + (expirationMinutes * 60 * 1000);
  const item = {
    value,
    expiration: expirationTime,
  };
  
  return setToStorage(key, item);
}

export function getWithExpiration<T>(
  key: string,
  defaultValue: T
): T {
  const item = getFromStorage(key, null);
  
  if (!item || !item.expiration) {
    return defaultValue;
  }
  
  if (new Date().getTime() > item.expiration) {
    removeFromStorage(key);
    return defaultValue;
  }
  
  return item.value;
}
```

## Constants and Configuration

### Application Constants
```typescript
// API configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

// WebSocket configuration
export const WEBSOCKET_CONFIG = {
  URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  RECONNECT_ATTEMPTS: 5,
  RECONNECT_DELAY: 3000,
  HEARTBEAT_INTERVAL: 30000,
} as const;

// UI constants
export const UI_CONFIG = {
  ANIMATION_DURATION: 300,
  DEBOUNCE_DELAY: 500,
  PAGINATION_SIZE: 20,
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
} as const;

// Validation constants
export const VALIDATION_RULES = {
  EMAIL_MAX_LENGTH: 320,
  PASSWORD_MIN_LENGTH: 8,
  USERNAME_MIN_LENGTH: 3,
  USERNAME_MAX_LENGTH: 30,
} as const;

// System constants
export const SYSTEM_CONFIG = {
  SUPPORTED_FILE_TYPES: ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt'],
  MAX_UPLOAD_SIZE: 50 * 1024 * 1024, // 50MB
  SESSION_TIMEOUT: 24 * 60 * 60 * 1000, // 24 hours
} as const;
```

### Error Messages
```typescript
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Internal server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  FILE_TOO_LARGE: 'File size exceeds the maximum allowed size.',
  UNSUPPORTED_FILE_TYPE: 'This file type is not supported.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',
} as const;
```

## Type Definitions

### Utility Types
```typescript
// API types
export interface ApiResponse<T> {
  data: T | null;
  success: boolean;
  error?: string;
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  data?: any;
  headers?: Record<string, string>;
  timeout?: number;
}

// Validation types
export interface ValidationRule {
  code: string;
  validate: (value: any) => ValidationResult;
}

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// Storage types
export interface StorageItem<T> {
  value: T;
  expiration?: number;
}

// Common utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K;
}[keyof T];
```

## Testing Utilities

### Test Helpers
```typescript
// Mock data generators
export function generateMockUser(): User {
  return {
    id: Math.random().toString(36).substr(2, 9),
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date().toISOString(),
  };
}

export function generateMockApiResponse<T>(
  data: T,
  success: boolean = true
): ApiResponse<T> {
  return {
    data: success ? data : null,
    success,
    error: success ? undefined : 'Mock error',
  };
}

// Test utilities
export function waitFor(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function createMockEvent(
  type: string,
  properties: Record<string, any> = {}
): Event {
  const event = new Event(type);
  Object.assign(event, properties);
  return event;
}
```

## Performance Utilities

### Optimization Helpers
```typescript
// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

// Throttle utility
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let isThrottled = false;
  
  return (...args: Parameters<T>) => {
    if (!isThrottled) {
      func(...args);
      isThrottled = true;
      setTimeout(() => {
        isThrottled = false;
      }, delay);
    }
  };
}

// Memoization utility
export function memoize<T extends (...args: any[]) => any>(
  func: T
): T {
  const cache = new Map();
  
  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = func(...args);
    cache.set(key, result);
    return result;
  }) as T;
}
```

## Development Standards

### Code Quality
- **TypeScript**: Full type safety for all utilities
- **Pure Functions**: Favor pure functions over side effects
- **Error Handling**: Comprehensive error handling
- **Documentation**: Clear JSDoc comments

### Testing
- **Unit Tests**: Test all utility functions
- **Edge Cases**: Test boundary conditions
- **Performance**: Test performance-critical utilities
- **Type Safety**: Test TypeScript type definitions

### Performance
- **Efficiency**: Optimize for common use cases
- **Memory**: Avoid memory leaks
- **Caching**: Use caching where appropriate
- **Lazy Loading**: Load utilities on demand

This comprehensive utility system provides a solid foundation for common functionality throughout the Overseer desktop application, promoting code reuse and maintainability.
