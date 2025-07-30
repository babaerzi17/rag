# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a knowledge management system built with a Tauri + Vue.js frontend and designed to implement a high-precision RAG (Retrieval-Augmented Generation) system. The project is currently in the frontend implementation phase.

## Development Commands

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Development server (Vite dev server on port 1420)
npm run dev

# Build for production
npm run build

# Type checking
npm run build  # includes vue-tsc type checking

# Tauri development (desktop app)
npm run tauri:dev

# Build Tauri app
npm run tauri:build

# Preview production build
npm run preview
```

### Project Structure Commands
```bash
# The project uses a specific port for Tauri
# Development server runs on http://localhost:1420

# Frontend source is in frontend/src/
# Main entry point: frontend/src/main.ts
# App component: frontend/src/App.vue
```

## Code Architecture

### Frontend Architecture
- **Framework**: Vue 3 with TypeScript and Composition API
- **Build Tool**: Vite with Tauri configuration
- **UI Library**: Vuetify 3 with Material Design Icons
- **State Management**: Pinia stores for auth and app state
- **Routing**: Vue Router with authentication guards and permission-based access
- **Desktop Integration**: Tauri for native desktop functionality

### Key Architectural Patterns

#### Component Structure
- **Layout Components**: `MainLayout.vue` and `AuthLayout.vue` provide the main application shells
- **View Components**: Lazy-loaded pages in `views/` directory organized by feature
- **Route-based Code Splitting**: All views are dynamically imported for optimal loading

#### State Management with Pinia
- **Auth Store** (`stores/auth.ts`): Manages user authentication, permissions, and roles
- **App Store** (`stores/app.ts`): Handles global app state like theme, sidebar, and user preferences
- **Permission System**: Role-based access control (RBAC) with permission checking

#### Routing Architecture  
- **Nested Routes**: Main app routes nested under `MainLayout`, auth routes under `AuthLayout`
- **Route Guards**: Authentication and permission checks in `router.beforeEach`
- **Meta Information**: Routes include title, icon, permission requirements
- **Permission-Based Navigation**: Routes are filtered based on user permissions

### Technology Integration

#### Tauri Configuration
- **Fixed Port**: Development server runs on port 1420 (required by Tauri)
- **Environment Variables**: Supports `VITE_` and `TAURI_` prefixed variables
- **Build Targets**: Chrome 105+ for Windows, Safari 13+ for other platforms
- **Debug Mode**: Conditional minification and sourcemap generation

#### Vue 3 Features
- **Composition API**: Used throughout with `<script setup>` syntax
- **TypeScript**: Full TypeScript integration with strict type checking
- **Vuetify Integration**: Material Design 3 with custom theme configuration
- **Global Styles**: Custom scrollbar, LaTeX math rendering, code highlighting

#### Special Features
- **LaTeX Support**: KaTeX integration for mathematical content rendering
- **Code Highlighting**: highlight.js for syntax highlighting
- **Responsive Design**: Custom CSS utilities and Vuetify responsive system
- **Theme System**: Light/dark mode with persistent user preferences

### Backend Architecture (Planned)
The system is designed for integration with a Python FastAPI backend featuring:
- **RAG System**: Multi-strategy retrieval including Fusion, Document Augmentation, Context Enriched
- **Vector Database**: ChromaDB for semantic search
- **Document Processing**: Support for various document formats with OCR
- **Authentication**: JWT-based auth with RBAC permission system

## Important Development Notes

### Authentication System
- Mock authentication is currently implemented in `stores/auth.ts`
- The system expects JWT tokens and user objects with roles/permissions
- All authenticated routes require the `requiresAuth: true` meta property
- Permission-based access uses the `permission` meta property

### Route Development
- New routes should follow the existing pattern in `router/index.ts`
- Add appropriate meta information (title, icon, permissions)
- Use lazy loading for all view components
- Implement proper TypeScript types for route meta

### State Management Patterns
- Use Pinia composition API style (`defineStore` with setup function)
- Persistent state (theme, user preferences) should use localStorage
- Authentication state should be initialized on app startup

### Styling Conventions
- Global styles are defined in `App.vue`
- Use Vuetify's design system and utilities
- Custom CSS utilities follow the pattern in the global styles
- Maintain responsive design principles

### Component Development
- Use Vue 3 Composition API with `<script setup>`
- Implement proper TypeScript interfaces for props and emits
- Follow the existing component organization pattern
- Use Vuetify components for consistency

### Development Workflow
The project appears to follow a phased development approach as outlined in the design documents, with frontend implementation currently in progress and backend RAG system planned for subsequent phases.