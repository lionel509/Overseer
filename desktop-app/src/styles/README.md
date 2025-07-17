# Styles System

## Overview

The styles directory contains all styling-related files for the Overseer desktop application. This includes global styles, theme definitions, component-specific styles, and utility classes built with Tailwind CSS and modern CSS features.

## Style Architecture

### Directory Structure

```
styles/
├── globals.css         # Global styles and CSS reset
├── themes/            # Theme definitions and variables
├── components/        # Component-specific styles
├── utilities/         # Utility classes and mixins
├── animations/        # Animation definitions
├── responsive/        # Responsive design utilities
└── variables.css      # CSS custom properties
```

## Styling System

### 1. Global Styles (`globals.css`)

#### CSS Reset and Normalize
- **Purpose**: Consistent cross-browser styling foundation
- **Features**: Modern CSS reset, normalized defaults
- **Compatibility**: Cross-browser compatibility fixes
- **Typography**: Base typography and font loading

#### Global Classes
- **Purpose**: Application-wide utility classes
- **Features**: Layout helpers, common patterns
- **Accessibility**: Focus indicators, screen reader utilities
- **Performance**: Optimized global styles

### 2. Theme System (`/themes/`)

#### Theme Variables
- **Purpose**: Centralized theme configuration
- **Features**: CSS custom properties, dynamic switching
- **Themes**: Light mode, dark mode, system preference
- **Customization**: User-customizable theme options

#### Color System
- **Purpose**: Consistent color palette across the app
- **Features**: Semantic color tokens, accessibility compliance
- **Variants**: Primary, secondary, accent, neutral colors
- **States**: Hover, active, disabled, focus states

#### Typography Scale
- **Purpose**: Harmonious typography system
- **Features**: Responsive font sizes, line heights
- **Hierarchy**: Heading levels, body text, captions
- **Fonts**: System fonts with fallbacks

### 3. Component Styles (`/components/`)

#### Scoped Styles
- **Purpose**: Component-specific styling
- **Features**: CSS Modules, scoped selectors
- **Isolation**: Style encapsulation, no conflicts
- **Maintainability**: Co-located with components

#### Component Variants
- **Purpose**: Flexible component styling
- **Features**: Size variants, state variations
- **Customization**: Props-based styling
- **Composition**: Composable style patterns

### 4. Utilities (`/utilities/`)

#### Tailwind Extensions
- **Purpose**: Custom utility classes
- **Features**: Application-specific utilities
- **Performance**: Optimized utility generation
- **Consistency**: Unified spacing and sizing

#### Helper Classes
- **Purpose**: Common styling patterns
- **Features**: Layout helpers, text utilities
- **Accessibility**: ARIA-friendly utilities
- **Responsive**: Mobile-first utilities

## Theme Implementation

### CSS Custom Properties
```css
:root {
  /* Color System */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-active: #1d4ed8;
  
  --color-secondary: #64748b;
  --color-secondary-hover: #475569;
  --color-secondary-active: #334155;
  
  --color-accent: #10b981;
  --color-accent-hover: #059669;
  --color-accent-active: #047857;
  
  /* Background Colors */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  
  /* Text Colors */
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --text-tertiary: #64748b;
  
  /* Border Colors */
  --border-primary: #e2e8f0;
  --border-secondary: #cbd5e1;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  
  /* Spacing System */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Typography */
  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  
  /* Border Radius */
  --radius-sm: 0.125rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-base: 200ms ease-in-out;
  --transition-slow: 300ms ease-in-out;
}
```

### Dark Theme Override
```css
[data-theme="dark"] {
  /* Background Colors */
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  
  /* Text Colors */
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;
  
  /* Border Colors */
  --border-primary: #334155;
  --border-secondary: #475569;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.5);
}
```

## Component Styling Examples

### Button Component Styles
```css
.button {
  /* Base styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: var(--transition-fast);
  cursor: pointer;
  border: 1px solid transparent;
  
  /* Focus styles */
  &:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
  
  /* Variants */
  &.primary {
    background-color: var(--color-primary);
    color: white;
    
    &:hover {
      background-color: var(--color-primary-hover);
    }
    
    &:active {
      background-color: var(--color-primary-active);
    }
  }
  
  &.secondary {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    border-color: var(--border-primary);
    
    &:hover {
      background-color: var(--bg-tertiary);
    }
  }
  
  &.ghost {
    background-color: transparent;
    color: var(--text-primary);
    
    &:hover {
      background-color: var(--bg-secondary);
    }
  }
  
  /* Sizes */
  &.small {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
  
  &.large {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: var(--font-size-lg);
  }
  
  /* States */
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  &.loading {
    position: relative;
    color: transparent;
    
    &::after {
      content: '';
      position: absolute;
      width: 1rem;
      height: 1rem;
      border: 2px solid transparent;
      border-top-color: currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }
}
```

### Card Component Styles
```css
.card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: var(--transition-base);
  
  &:hover {
    box-shadow: var(--shadow-md);
  }
  
  &.interactive {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
  }
  
  .card-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-primary);
    
    .card-title {
      margin: 0;
      font-size: var(--font-size-xl);
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .card-subtitle {
      margin: var(--spacing-xs) 0 0;
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
    }
  }
  
  .card-content {
    padding: var(--spacing-lg);
  }
  
  .card-footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--border-primary);
    background-color: var(--bg-secondary);
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  }
}
```

## Animation System

### Keyframes
```css
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-in-right {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
```

### Animation Utilities
```css
.animate-spin {
  animation: spin 1s linear infinite;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-in {
  animation: slide-in-right 0.2s ease-out;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

## Responsive Design

### Breakpoint System
```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}

/* Media Query Mixins */
@media (min-width: 640px) {
  .sm\:block {
    display: block;
  }
  
  .sm\:flex {
    display: flex;
  }
  
  .sm\:hidden {
    display: none;
  }
}

@media (min-width: 768px) {
  .md\:grid {
    display: grid;
  }
  
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .md\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
  
  .lg\:text-lg {
    font-size: var(--font-size-lg);
  }
}
```

### Container Queries
```css
.dashboard-grid {
  container-type: inline-size;
}

@container (min-width: 300px) {
  .metric-card {
    flex-direction: row;
  }
}

@container (min-width: 500px) {
  .metric-card {
    padding: var(--spacing-lg);
  }
}
```

## Accessibility Styles

### Focus Management
```css
.focus-ring {
  &:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
}

.focus-ring-inset {
  &:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: -2px;
  }
}
```

### Screen Reader Utilities
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.not-sr-only {
  position: static;
  width: auto;
  height: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

### High Contrast Mode
```css
@media (prefers-contrast: high) {
  :root {
    --color-primary: #0000ff;
    --color-accent: #008000;
    --text-primary: #000000;
    --bg-primary: #ffffff;
    --border-primary: #000000;
  }
}
```

## Performance Optimization

### CSS Optimization
- **Critical CSS**: Inline critical styles
- **Code Splitting**: Lazy load non-critical styles
- **Minification**: Compressed CSS output
- **Purging**: Remove unused styles

### Loading Strategy
- **Preload**: Preload critical fonts and styles
- **Fallbacks**: System font fallbacks
- **Progressive Enhancement**: Layer additional styles
- **Caching**: Optimize CSS caching

## Development Workflow

### Build Process
- **PostCSS**: Modern CSS processing
- **Autoprefixer**: Automatic vendor prefixes
- **CSS Modules**: Scoped styling
- **Tailwind CSS**: Utility-first framework

### Development Tools
- **Hot Reload**: Instant style updates
- **Source Maps**: Debug-friendly CSS
- **Linting**: StyleLint for code quality
- **Formatting**: Prettier for consistency

### Design Tokens
- **Centralized**: Single source of truth
- **Automated**: Token generation from design
- **Consistent**: Cross-platform consistency
- **Maintainable**: Easy updates and changes

## Future Enhancements

### Advanced Features
- **CSS-in-JS**: Runtime styling capabilities
- **Design System**: Component-based design system
- **Theming**: Advanced theming capabilities
- **Animations**: Complex animation system

### Performance
- **Critical CSS**: Automatic critical CSS extraction
- **Tree Shaking**: Dead code elimination
- **Compression**: Advanced compression techniques
- **Caching**: Intelligent caching strategies

This comprehensive styling system provides a solid foundation for creating a beautiful, consistent, and maintainable user interface for the Overseer desktop application.
