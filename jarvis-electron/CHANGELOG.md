# Changelog

All notable changes to the Jarvis Desktop project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2026-11-19

### Added
- **KARION Mobile Protocol Bridge**: Integrated end-to-end encrypted synchronization with KARION Android devices.
- **Mobile Bridge HUD Panel** (`src/components/KarionPanel.tsx`): 
  - Real-time Firestore synchronization for call requests, tasks, and focus sessions.
  - Interactive phone dialer with agent script dispatch (VOICE_AGENT_TURN).
  - PC-side task verification and approval for encrypted Android tasks.
  - Focus session monitoring and "Strict Lock" remote arming.
- **Settings & Pairing**: 
  - New "KARION Mobile Pairing" section in Settings with Firebase config, Operator UID, and AES-256-GCM E2EE session key support.
  - Secure storage of E2EE keys in Electron's `userData` path, isolated from the renderer process.
  - LLM Base URL preset toggle (Local FreeLLMAPI `http://127.0.0.1:31415` vs Custom).
- **Assistant Tools**: Registered `place_phone_call`, `hang_up_call`, `check_phone_balance`, `approve_android_task`, and `toggle_phone_focus_lock` as callable tools in the assistant chat pipeline.

### Changed
- **Package Version**: Bumped to 2.4.0.
- **Sidebar Navigation**: Added "Mobile Bridge" as a top-level navigation item.

## [2.3.0] - 2026-11-19

### Changed
- **LLM Backend Migration**: Default API base URL updated from `http://localhost:8000` to `http://127.0.0.1:31415` (freellmapi service)
- **API Key Handling**: Chat requests now send `Authorization: Bearer <key>` header from stored LLM credentials when available

### Fixed
- **Connection Error Messaging**: Replaced hardcoded "ensure python api/main.py is running on localhost:8000" with actionable diagnostics showing active base URL and settings guidance
- **Type Safety**: Fixed TypeScript error in API request headers by properly casting option headers

## [2.2.0] - 2026-11-18

### Fixed
- **UI Overflow**: Applied `overflow-y-auto` to all main workspace panels (Settings, Agents, Integrations) to prevent content clipping
- **Composio Binding**: Implemented proper account selection modal flow for OAuth instead of silent failure
- **Backend Management**: Added IPC lifecycle control (`launch`/`stop`/`status`) and integrated frontend controls to launch the Python API backend
- **Voice Pipeline**: Fixed missing `voiceSTT` store state and properly gated Web Speech API "Hey Jarvis" wake-word processing

## [2.1.0] - 2026-11-18

### Added

#### Settings & API Configuration
- **API Credentials Panel**: New "Auth" settings section with secure password-input fields for OpenAI/Custom LLM key, Composio API key, STT key, and TTS key
- **Local Persistence**: API keys stored in localStorage with IPC broadcast via preload bridge (`api-keys-updated`)
- **Save Confirmation**: Visual feedback toast ("✓ CREDENTIALS SAVED LOCALLY") on each save

#### Composio Integration
- **Agents Panel** (`src/components/AgentsPanel.tsx`): Full replacement of "coming soon" placeholder
  - Composio API key input with show/hide toggle and local persistence
  - Per-app connection state cards (Twitter/X, LinkedIn, Facebook, Instagram) mirroring parent project's `socials.js` / `connect.js` app definitions
  - Simulated OAuth handshake with loading/error states
  - Live notification feedback on connect/disconnect

- **Integrations Panel** (`src/components/IntegrationsPanel.tsx`): Full replacement of "coming soon" placeholder
  - Backend health polling (every 5s) with WebSocket online/offline indicator chip
  - Service catalog showing all four social apps with read-only descriptors
  - Tool execution log panel — append-only, capped at 50 entries, clearable
  - Quick-action buttons to run sample queries per platform

#### Voice Pipeline Improvements
- **ChatPanel Error Handling**: Distinguishes network errors ("Backend unreachable — ensure python api/main.py is running") from API errors, sets correct hologram state (`ERROR` vs `IDLE`)
- **WebSocket Health Monitor**: Integrations panel polls `/health` every 5 seconds

### Changed

- **App.tsx Section Registry**: `agents` → `<AgentsPanel />`, `integrations` → `<IntegrationsPanel />` (both previously rendered `PlaceholderSection`)
- **Version**: Bumped from 2.0.0 to 2.1.0

### Fixed

- Improved error messages for unresponsive backend so users know exactly what to check

---



### Added

#### UI/UX Overhaul
- **Complete Stark Industries HUD Design System**: Migrated all visual elements from JARVIS-Command-Center reference project
- **Centralized Design Token System**: Unified CSS custom properties for consistent theming (--cyan, --panel, --line, etc.)
- **New Sidebar Component**: Fixed layout issues with proper flex/grid stacking and distinct HUD styling
- **Main Content Dashboard**: Replaced flat dark void with high-density multi-pane sci-fi dashboard
- **Window Framing**: Removed bulky native OS chrome, added minimal Stark Industries top-bar controls
- **Command Dock**: Implemented fixed-position command input bar at bottom center of viewport
- **Ambient Background Layers**: Added grid overlay and grain texture for authentic HUD feel
- **Live Clock**: Real-time clock display in footer with formatted time updates

#### Components
- **HomeDashboardPanel**: Full HUD dashboard with hologram projection stage, power meter, directives list, activity stream
- **TasksPanel**: Overview-grid pattern with task-full rows and approvals section
- **DevicesPanel**: Device-grid with 6 status cards preserving Sims/balance logic
- **ActivityPanel**: Notification stream with type-based color coding (error/warning/success/info)
- **SettingsPanel**: 3-column settings grid (Voice/Appearance/Backend config) with toggle objects
- **ChatPanel**: Preserves full API integration (api.call, api.balance, api.hangup, api.status, api.processVoiceCommand)
- **Hologram.tsx**: Dynamic Three.js import with state lerp colors for IDLE/LISTENING/THINKING/SPEAKING/WORKING/ERROR states
- **Sidebar.tsx**: Complete navigation with brand mark, nav items, connection status, and version info

#### Infrastructure
- **TypeScript Integration**: Full type-safe interfaces for SystemStatus, DeviceStatus, Notification, Task, HologramState
- **Tailwind Configuration**: Extended theme with design tokens, custom colors, and fonts (Barlow Condensed + Space Grotesk)
- **Global CSS Architecture**: Modular CSS organization with component-specific rules

### Changed

- **Architecture**: Migrated from generic grid layout to source-project's position:fixed sidebar pattern
- **State Management**: Enhanced Zustand store with comprehensive typing
- **API Integration**: Updated to use correct api.processVoiceCommand() signature instead of deprecated call() format
- **Build Process**: Optimized Vite configuration for Electron development pipeline
- **Dependencies**: Added Tailwind CSS integration, refined package structure

### Fixed

- **Sidebar Layout**: Resolved text overlapping and spacing issues in navigation items
- **Layout Calculations**: Corrected CommandDock horizontal positioning from broken Tailwind arbitrary values to proper CSS calc formula
- **Missing CSS Classes**: Added all ~150+ missing CSS rules for sidebar, panels, command dock, device grids, and responsive breakpoints
- **TypeScript Errors**: Eliminated all type mismatches and invalid API calls
- **Import Paths**: Standardized service imports to use correct './services/api' path

### Removed

- **Legacy Grid Layout**: Removed old CSS grid approach that conflicted with source design patterns
- **Obsolete API Calls**: Replaced incorrect api.call({ message }) usage with proper api.processVoiceCommand(text)

## [1.0.0] - Initial Release

### Added
- Basic Electron application structure
- React frontend with Vite build system
- Zustand state management
- TypeScript configuration
- Hologram component with Three.js integration
- Basic chat interface
- Device status monitoring
- Simple task management
- Settings panel

---

## Version Notes

**2.0.0** represents a complete UI redesign aligned with the Stark Industries Command Center aesthetic while preserving all backend functionality and state management logic from v1.0.0.

The migration maintains full compatibility with the existing Python FastAPI backend (localhost:8000) and all IPC handlers remain intact.
