# JARVIS_DEPENDENCY_AND_LICENSE_MAP.md

## Dependency Map

### Python Dependencies
| Package | Version | Purpose | License |
|---|---|---|---|
| FastAPI | latest | REST API framework | MIT |
| Pydantic | latest | Request validation | MIT |
| Uvicorn | latest | ASGI server | MIT |
| Aiohttp | latest | Async HTTP client | Apache 2.0 |
| Subprocess | built-in | ADB command execution | Python |

### JavaScript/Node.js Dependencies (Roamies)
| Package | Version | Purpose | License |
|---|---|---|---|
| Express | latest | HTTP server | MIT |
| Socket.io | latest | Real-time communication | MIT |
| WS | latest | WebSocket library | MIT |
| Node-fetch | latest | HTTP client | MIT |

### System Dependencies
| Tool | Version | Purpose | License |
|---|---|---|---|
| ADB | latest | Android Debug Bridge | Apache 2.0 |
| Python | 3.9+ | Runtime | Python |
| Node.js | 18+ | Sidecar runtime | MIT |
| Rust | latest | Tauri build | MIT |

## License Map

### AGPL-3.0 Components
| Component | Source | Obligations |
|---|---|---|
| Roamies | KenKaiii/Roamies | Must release source if distributed or network service |
| Roamies Sidecar | showcase/tauri/sidecar | Must release source if modified |
| Roamies Tauri | showcase/tauri/src-tauri | Must release source if modified |

### MIT Components
| Component | Source | Obligations |
|---|---|---|
| FastAPI | FastAPI | Permissive, attribution required |
| Pydantic | Pydantic | Permissive, attribution required |
| Uvicorn | Uvicorn | Permissive, attribution required |

### Apache 2.0 Components
| Component | Source | Obligations |
|---|---|---|
| Aiohttp | Aiohttp | Permissive, patent grant |
| ADB | Google | Permissive, patent grant |

## License Compliance Strategy

### Internal Use
- Existing Python services remain proprietary
- No source code disclosure required

### Network Service
- If FastAPI endpoints are exposed publicly, AGPL-3.0 applies
- Must release source code of modified Roamies components

### Distribution
- If distributing the application, must release source code
- Must include AGPL-3.0 license and attribution

## Risk Mitigation

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| API integration failures | Medium | High | Thorough testing, fallback mechanisms |
| Permission conflicts | Low | Medium | Clear permission boundaries |
| Performance degradation | Low | High | Load testing, optimization |
| Security vulnerabilities | Low | Critical | Regular security audits |

### License Risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| AGPL-3.0 compliance | Medium | High | Legal review, clear boundaries |
| Dependency conflicts | Low | Medium | Version pinning, testing |

## Implementation Checklist

### Phase 1: Foundation
- [ ] Set up FastAPI service
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Test endpoints

### Phase 2: AI Integration
- [ ] Implement Roamies bridge
- [ ] Register tools
- [ ] Add voice capabilities
- [ ] Implement memory system

### Phase 3: Features
- [ ] Integrate Gmail
- [ ] Integrate Calendar
- [ ] Add Telegram
- [ ] Add SMS
- [ ] Add scheduler
- [ ] Add automation

### Phase 4: Security
- [ ] Implement permissions
- [ ] Add audit logging
- [ ] Set up validation
- [ ] Review compliance

### Phase 5: Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Security tests
- [ ] Performance tests