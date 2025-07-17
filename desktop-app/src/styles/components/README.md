# Component Styles

## Overview

The component styles directory contains CSS modules and component-specific styling for the Overseer desktop application. These styles are designed to work alongside the global theme system while providing scoped, maintainable styling for individual components.

## Organization

### Style Categories

```
components/
├── atoms/           # Atomic component styles
├── molecules/       # Molecular component styles
├── organisms/       # Organism component styles
├── layouts/         # Layout component styles
├── common/          # Shared component styles
└── mixins/          # Reusable CSS mixins
```

## Atomic Component Styles

### Button Styles (`atoms/Button.module.css`)
```css
.button {
  /* Base button styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  line-height: 1.5;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
  
  /* Focus styles */
  &:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
}

.primary {
  background-color: var(--color-primary);
  color: white;
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary-hover);
  }
  
  &:active:not(:disabled) {
    background-color: var(--color-primary-active);
    transform: translateY(1px);
  }
}

.secondary {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-primary);
  
  &:hover:not(:disabled) {
    background-color: var(--bg-tertiary);
    border-color: var(--border-secondary);
  }
}

.ghost {
  background-color: transparent;
  color: var(--text-primary);
  
  &:hover:not(:disabled) {
    background-color: var(--bg-secondary);
  }
}

.danger {
  background-color: var(--color-danger);
  color: white;
  
  &:hover:not(:disabled) {
    background-color: var(--color-danger-hover);
  }
}

/* Size variants */
.small {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.large {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-lg);
}

.icon {
  padding: var(--spacing-sm);
  aspect-ratio: 1;
}

/* State styles */
.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.loading {
  position: relative;
  color: transparent;
  
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 1rem;
    height: 1rem;
    margin: -0.5rem 0 0 -0.5rem;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}
```

### Input Styles (`atoms/Input.module.css`)
```css
.input {
  /* Base input styles */
  display: block;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--font-size-base);
  line-height: 1.5;
  transition: all var(--transition-fast);
  
  &::placeholder {
    color: var(--text-tertiary);
  }
  
  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-alpha);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background-color: var(--bg-secondary);
  }
}

.error {
  border-color: var(--color-danger);
  
  &:focus {
    border-color: var(--color-danger);
    box-shadow: 0 0 0 3px var(--color-danger-alpha);
  }
}

.success {
  border-color: var(--color-success);
  
  &:focus {
    border-color: var(--color-success);
    box-shadow: 0 0 0 3px var(--color-success-alpha);
  }
}

.small {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.large {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-lg);
}

.withIcon {
  padding-left: calc(var(--spacing-md) + 1.5rem);
}

.withClearButton {
  padding-right: calc(var(--spacing-md) + 1.5rem);
}
```

### Icon Styles (`atoms/Icon.module.css`)
```css
.icon {
  /* Base icon styles */
  display: inline-block;
  width: 1em;
  height: 1em;
  vertical-align: middle;
  fill: currentColor;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.small {
  width: 0.75em;
  height: 0.75em;
}

.large {
  width: 1.25em;
  height: 1.25em;
}

.xlarge {
  width: 1.5em;
  height: 1.5em;
}

.interactive {
  cursor: pointer;
  
  &:hover {
    transform: scale(1.1);
  }
  
  &:active {
    transform: scale(0.95);
  }
}

.spinning {
  animation: spin 1s linear infinite;
}

.pulse {
  animation: pulse 2s infinite;
}
```

## Molecular Component Styles

### Card Styles (`molecules/Card.module.css`)
```css
.card {
  /* Base card styles */
  background-color: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: all var(--transition-base);
}

.interactive {
  cursor: pointer;
  
  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.compact {
  box-shadow: none;
  border-radius: var(--radius-md);
}

.elevated {
  box-shadow: var(--shadow-lg);
  
  &:hover {
    box-shadow: var(--shadow-xl);
  }
}

.header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-primary);
  background-color: var(--bg-secondary);
}

.title {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
}

.subtitle {
  margin: var(--spacing-xs) 0 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.content {
  padding: var(--spacing-lg);
}

.footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-primary);
  background-color: var(--bg-secondary);
}

.actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
}
```

### SearchBar Styles (`molecules/SearchBar.module.css`)
```css
.searchBar {
  /* Base search bar styles */
  position: relative;
  width: 100%;
  max-width: 400px;
}

.input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  padding-left: calc(var(--spacing-md) + 1.5rem);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--font-size-base);
  transition: all var(--transition-fast);
  
  &::placeholder {
    color: var(--text-tertiary);
  }
  
  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-alpha);
  }
}

.icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
}

.clearButton {
  position: absolute;
  right: var(--spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  padding: var(--spacing-xs);
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
  
  &:hover {
    background-color: var(--bg-secondary);
    color: var(--text-secondary);
  }
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  margin-top: var(--spacing-xs);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 300px;
  overflow-y: auto;
}

.suggestion {
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  
  &:hover,
  &:focus {
    background-color: var(--bg-secondary);
    outline: none;
  }
  
  &.active {
    background-color: var(--color-primary);
    color: white;
  }
}

.noResults {
  padding: var(--spacing-md);
  color: var(--text-tertiary);
  text-align: center;
  font-style: italic;
}
```

## Organism Component Styles

### Dashboard Styles (`organisms/Dashboard.module.css`)
```css
.dashboard {
  /* Base dashboard styles */
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  min-height: 100vh;
}

.header {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) 0;
  border-bottom: 1px solid var(--border-primary);
  margin-bottom: var(--spacing-lg);
}

.title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.actions {
  display: flex;
  gap: var(--spacing-sm);
}

.widget {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.widget:hover {
  box-shadow: var(--shadow-md);
}

.widgetHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.widgetTitle {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.widgetActions {
  display: flex;
  gap: var(--spacing-xs);
}

.widgetContent {
  color: var(--text-secondary);
}

.metric {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-primary);
  
  &:last-child {
    border-bottom: none;
  }
}

.metricIcon {
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
}

.metricContent {
  flex: 1;
}

.metricLabel {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin: 0;
}

.metricValue {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.metricChange {
  font-size: var(--font-size-sm);
  font-weight: 500;
  
  &.positive {
    color: var(--color-success);
  }
  
  &.negative {
    color: var(--color-danger);
  }
  
  &.neutral {
    color: var(--text-tertiary);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
  }
  
  .header {
    flex-direction: column;
    gap: var(--spacing-md);
    text-align: center;
  }
  
  .actions {
    justify-content: center;
  }
}
```

## Layout Component Styles

### MainLayout Styles (`layouts/MainLayout.module.css`)
```css
.layout {
  /* Base layout styles */
  display: grid;
  grid-template-areas: 
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 250px 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
  background-color: var(--bg-secondary);
}

.header {
  grid-area: header;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
  z-index: 100;
}

.sidebar {
  grid-area: sidebar;
  background-color: var(--bg-primary);
  border-right: 1px solid var(--border-primary);
  overflow-y: auto;
  transition: transform var(--transition-base);
}

.main {
  grid-area: main;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.footer {
  grid-area: footer;
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-primary);
  padding: var(--spacing-md) var(--spacing-lg);
  text-align: center;
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

/* Collapsed sidebar */
.sidebarCollapsed {
  transform: translateX(-100%);
}

.layoutCollapsed {
  grid-template-columns: 0 1fr;
}

/* Mobile layout */
@media (max-width: 768px) {
  .layout {
    grid-template-areas: 
      "header"
      "main"
      "footer";
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 250px;
    height: 100vh;
    z-index: 200;
    transform: translateX(-100%);
    
    &.sidebarOpen {
      transform: translateX(0);
    }
  }
  
  .main {
    padding: var(--spacing-md);
  }
}
```

## Common Styles

### Utility Classes (`common/utilities.module.css`)
```css
/* Visibility utilities */
.hidden {
  display: none;
}

.visible {
  display: block;
}

.visuallyHidden {
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

/* Flexbox utilities */
.flex {
  display: flex;
}

.flexColumn {
  flex-direction: column;
}

.flexCenter {
  align-items: center;
  justify-content: center;
}

.flexBetween {
  justify-content: space-between;
}

.flexEnd {
  justify-content: flex-end;
}

.flexWrap {
  flex-wrap: wrap;
}

.flexGrow {
  flex-grow: 1;
}

/* Grid utilities */
.grid {
  display: grid;
}

.gridCols2 {
  grid-template-columns: repeat(2, 1fr);
}

.gridCols3 {
  grid-template-columns: repeat(3, 1fr);
}

.gridCols4 {
  grid-template-columns: repeat(4, 1fr);
}

.gridGap {
  gap: var(--spacing-md);
}

/* Text utilities */
.textCenter {
  text-align: center;
}

.textLeft {
  text-align: left;
}

.textRight {
  text-align: right;
}

.textTruncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.textWrap {
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Spacing utilities */
.m0 { margin: 0; }
.mt0 { margin-top: 0; }
.mr0 { margin-right: 0; }
.mb0 { margin-bottom: 0; }
.ml0 { margin-left: 0; }

.p0 { padding: 0; }
.pt0 { padding-top: 0; }
.pr0 { padding-right: 0; }
.pb0 { padding-bottom: 0; }
.pl0 { padding-left: 0; }

/* Border utilities */
.border {
  border: 1px solid var(--border-primary);
}

.borderTop {
  border-top: 1px solid var(--border-primary);
}

.borderBottom {
  border-bottom: 1px solid var(--border-primary);
}

.borderRadius {
  border-radius: var(--radius-md);
}

/* Background utilities */
.bgPrimary {
  background-color: var(--bg-primary);
}

.bgSecondary {
  background-color: var(--bg-secondary);
}

.bgTertiary {
  background-color: var(--bg-tertiary);
}

/* Animation utilities */
.fadeIn {
  animation: fadeIn 0.3s ease-out;
}

.slideIn {
  animation: slideIn 0.2s ease-out;
}

.bounceIn {
  animation: bounceIn 0.5s ease-out;
}

/* Interaction utilities */
.clickable {
  cursor: pointer;
  user-select: none;
}

.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.loading {
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.4),
      transparent
    );
    animation: shimmer 1.5s infinite;
  }
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}
```

## Development Standards

### CSS Modules
- **Scoped Styles**: All styles are scoped to components
- **Naming Convention**: camelCase for class names
- **Composition**: Use composes for style reuse
- **TypeScript**: Generate TypeScript definitions

### Performance
- **Critical CSS**: Inline critical component styles
- **Code Splitting**: Load component styles on demand
- **Caching**: Optimize style caching
- **Minification**: Compress CSS output

### Maintainability
- **Consistent Structure**: Follow established patterns
- **Documentation**: Document complex styles
- **Testing**: Visual regression testing
- **Linting**: CSS linting and formatting

This component styles system provides organized, maintainable, and performant styling for all UI components in the Overseer desktop application.
