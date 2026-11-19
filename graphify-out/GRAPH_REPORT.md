# Graph Report - Jarvis  (2026-11-16)

## Corpus Check
- 91 files · ~391,732 words
- Verdict: corpus is large enough that graph structure adds value.
- WARNING: 75 of 166 files seen (45%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 1269 nodes · 2193 edges · 152 communities (26 shown, 126 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 151 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Jarvis Core Brain & Orchestration
- Windows Desktop Client & UI
- Android Application & Remote Control
- Computer Use Engine & Automation
- Permission & Security Model
- Voice Speech Engine & TTS/STT
- Holographic Interface & 3D Rendering
- Roamies AI Orchestrator Integration
- FastAPI Service & Backend API
- Telephony & USSD Services
- Persistent Memory & Storage
- Platform Tools & Licenses
- Documentation & Architecture Specs
- Electron Desktop App
- Backend Services & Infrastructure
- Testing & Utilities
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 26
- Community 27
- Community 28
- Community 29
- Community 31
- Community 32
- Community 33
- Community 34
- Community 36
- Community 37
- Community 38
- Community 41
- Community 42
- Community 43
- Community 44
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 56
- Community 58
- Community 61
- Community 62
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150

## God Nodes (most connected - your core abstractions)
1. `JarvisVoiceIntegration` - 47 edges
2. `HologramRenderer3D` - 39 edges
3. `VoiceCommandProcessor` - 33 edges
4. `JarvisVoiceInterface` - 31 edges
5. `AndroidTelephonyAdapter` - 25 edges
6. `USSDManager` - 24 edges
7. `JarvisGUI` - 24 edges
8. `EnhancedJarvisGUI` - 23 edges
9. `EventBus` - 22 edges
10. `useJarvisStore` - 20 edges

## Surprising Connections (you probably didn't know these)
- `process_voice_command()` --uses--> `VoiceCommandProcessor`  [INFERRED]
  api/main.py → voice_command_processor.py
- `get_voice_status()` --uses--> `VoiceStatus`  [INFERRED]
  api/main.py → jarvis_voice_integration.py
- `get_sim_details()` --uses--> `AndroidTelephonyAdapter`  [INFERRED]
  api/main.py → core/telephony.py
- `get_sim_details()` --uses--> `USSDManager`  [INFERRED]
  api/main.py → core/ussd.py
- `initiate_call()` --uses--> `AndroidTelephonyAdapter`  [INFERRED]
  api/main.py → core/telephony.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Mobile App UI Layout Pattern** — screen_screenshot_jarvis_app_status_bar, screen_screenshot_jarvis_app_header, screen_screenshot_jarvis_app_main_content, screen_screenshot_jarvis_app_action_bar, screen_screenshot_jarvis_app_bottom_nav [EXTRACTED 1.00]
- **Voice AI Interaction Flow** — screen_screenshot_jarvis_app_action_bar, screen_screenshot_jarvis_app_voice_ai, screen_screenshot_jarvis_app_chat_interface [INFERRED 0.75]

## Communities (152 total, 126 thin omitted)

### Community 0 - "Jarvis Core Brain & Orchestration"
Cohesion: 0.06
Nodes (50): dependencies, react@^18.2.0, react-dom@^18.2.0, react-router-dom@^6.8.0, three@^0.160.0, zustand@^4.5.0, App(), HomeSection() (+42 more)

### Community 1 - "Windows Desktop Client & UI"
Cohesion: 0.05
Nodes (6): OCRProcessor, ScreenAnalyzer, ScreenCapture, UIElement, UIElementDetector, VisualCommandExecutor

### Community 2 - "Android Application & Remote Control"
Cohesion: 0.06
Nodes (5): get_command_processor(), CommandTemplate, main(), VoiceCommand, VoiceCommandProcessor

### Community 3 - "Computer Use Engine & Automation"
Cohesion: 0.05
Nodes (5): BackgroundJob, BackgroundJobManager, JobStatus, ScheduledTask, TaskManager

### Community 5 - "Voice Speech Engine & TTS/STT"
Cohesion: 0.08
Nodes (7): ModelAdapter, ModelConfig, JarvisOrchestrator, PlanStep, MultiStepReasoner, ToolRouter, test_orchestrator()

### Community 6 - "Holographic Interface & 3D Rendering"
Cohesion: 0.10
Nodes (9): main(), EventBus, HealthMonitor, JarvisLifecycle, create_jarvis_tool_registry(), main(), test_event_bus(), test_lifecycle() (+1 more)

### Community 7 - "Roamies AI Orchestrator Integration"
Cohesion: 0.10
Nodes (14): check_balance(), get_sim_details(), get_system_status(), get_telephony_service(), get_voice_help(), get_voice_history(), get_voice_integration(), get_voice_interface() (+6 more)

### Community 8 - "FastAPI Service & Backend API"
Cohesion: 0.12
Nodes (3): ToolResult, ToolRoute, ApprovalRequest

### Community 9 - "Telephony & USSD Services"
Cohesion: 0.08
Nodes (3): JARVISToolRegistry, ToolDefinition, ToolResult

### Community 10 - "Persistent Memory & Storage"
Cohesion: 0.12
Nodes (4): EnhancedJarvisGUI, main(), main(), demo_gui_integration()

### Community 11 - "Platform Tools & Licenses"
Cohesion: 0.14
Nodes (8): BalanceTool, BaseTool, CallTool, HangupTool, StatusTool, ToolSpec, USSDTool, _register_default_tools()

### Community 13 - "Electron Desktop App"
Cohesion: 0.10
Nodes (4): check_permission(), PermissionEngine, PermissionLevel, PermissionPolicy

### Community 14 - "Backend Services & Infrastructure"
Cohesion: 0.12
Nodes (22): description, devDependencies, autoprefixer@^10.4.0, postcss@^8.4.0, tailwindcss@^3.4.0, @types/node@^18.14.0, @types/react@^18.2.0, @types/react-dom@^18.2.0 (+14 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, baseUrl, forceConsistentCasingInFileNames, isolatedModules, jsx, lib, module (+12 more)

### Community 18 - "Community 18"
Cohesion: 0.21
Nodes (6): process_voice_command(), AndroidTelephonyAdapter, main(), speak_as_jarvis(), jarvis_speak(), main()

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (5): HologramState, demo_comprehensive(), demo_holographic_renderer(), demo_voice_integration(), main()

### Community 21 - "Community 21"
Cohesion: 0.16
Nodes (4): detect_network(), get_ussd_service(), USSDManager, TestUSSDConfigurationAndPrefixes

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (5): VoiceCommandSource, VoiceIntegrationMode, VoiceStatus, CommandPriority, CommandStatus

### Community 28 - "Community 28"
Cohesion: 0.17
Nodes (5): auth_health(), auth_root(), generate_token(), TokenManager, verify_token()

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (3): DetectionConfidence, ImageFormat, ScreenRegion

### Community 46 - "Community 46"
Cohesion: 0.22
Nodes (10): Jarvis Mobile App Screenshot, Action/Input Bar, Bottom Navigation Bar, Bottom Navigation Pattern, Chat Interface Pattern, Dark Theme Design, Header Area, Main Content Area (+2 more)

### Community 47 - "Community 47"
Cohesion: 0.22
Nodes (8): mcpServers, args, command, env, name, name, schema, version

### Community 48 - "Community 48"
Cohesion: 0.22
Nodes (5): electron_1, path_1, electron_1, electron@^28.3.3, electron

### Community 49 - "Community 49"
Cohesion: 0.22
Nodes (9): build, appId, directories, files, nsis, productName, output, artifactName (+1 more)

### Community 51 - "Community 51"
Cohesion: 0.25
Nodes (4): vite@^5.4.0, @vitejs/plugin-react@^4.7.0, vite, @vitejs/plugin-react

### Community 56 - "Community 56"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, start, typecheck

## Knowledge Gaps
- **84 isolated node(s):** `Apache License`, `ICU License`, `MIT License`, `BSD License`, `GNU General Public License` (+79 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 590 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **126 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JarvisVoiceIntegration` connect `Community 29` to `Community 34`, `Community 35`, `Android Application & Remote Control`, `Community 38`, `Roamies AI Orchestrator Integration`, `Persistent Memory & Storage`, `Community 45`, `Community 20`, `Community 22`, `Community 54`, `Community 58`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `JarvisVoiceIntegration` (e.g. with `EnhancedJarvisGUI` and `VoiceCommandProcessor`) actually correct?**
  _`JarvisVoiceIntegration` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Apache License`, `ICU License`, `MIT License` to the rest of the system?**
  _84 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Jarvis Core Brain & Orchestration` be split into smaller, more focused modules?**
  _Cohesion score 0.061668289516390785 - nodes in this community are weakly interconnected._
- **Why does `HologramRenderer3D` connect `Permission & Security Model` to `Community 41`, `Persistent Memory & Storage`, `Community 44`, `Community 20`, `Community 53`, `Community 22`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `VoiceCommandProcessor` (e.g. with `process_voice_command()` and `JarvisVoiceIntegration`) actually correct?**
  _`VoiceCommandProcessor` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Windows Desktop Client & UI` be split into smaller, more focused modules?**
  _Cohesion score 0.0523532522474881 - nodes in this community are weakly interconnected._