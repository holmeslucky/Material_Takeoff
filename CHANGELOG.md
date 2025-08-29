# Changelog

All notable changes to Capitol Takeoff will be documented in this file.

## [1.0.0] - 2025-01-23

### Added - Phase 5: AI Enhancement
- OpenAI GPT-4o-mini integration for proposal generation
- AI-powered proposal templates (Professional, Executive, Technical)
- Smart material suggestions based on project descriptions
- Takeoff optimization recommendations using AI
- Context-aware takeoff assistant chat interface
- Token usage tracking and cost estimation
- Fallback systems for AI service availability

### Added - Phase 3: Core Features
- Complete material database migration from SQLite to PostgreSQL
- 11-column takeoff entry system with real-time calculations
- Auto/Manual labor calculation modes with complexity analysis
- Project management system with CRUD operations
- Project duplication and statistics tracking
- Professional proposal generation service
- Material search and autocomplete functionality
- Real-time weight, pricing, and labor calculations

### Added - Phase 2: Web Infrastructure
- FastAPI backend with SQLAlchemy ORM and Pydantic validation
- React 18 frontend with TypeScript and Tailwind CSS
- Docker containerized development environment
- PostgreSQL database integration
- Nginx reverse proxy configuration
- Railway deployment configuration
- GitHub Actions CI/CD pipeline
- Environment configuration management

### Added - Phase 1: Foundation
- Working backups of desktop CustomTkinter application
- SQLite database backup for migration safety
- Feature baseline documentation
- Migration planning and architecture design

### Changed
- Port configuration updated: Frontend moved to port 7000
- All emojis removed from documentation and interface
- OpenAI API key auto-configuration in development startup

### Technical Details
- Backend: Python 3.11, FastAPI, PostgreSQL, SQLAlchemy
- Frontend: React 18, TypeScript, Tailwind CSS, Vite
- AI: OpenAI GPT-4o-mini with cost optimization
- Infrastructure: Docker, Nginx, Railway deployment ready
- Company: Full Capitol Engineering Company branding integration

### Migration Notes
- 100% feature parity with desktop application achieved
- All 1,918+ materials preserved with CWT pricing
- Desktop 11-column takeoff structure maintained exactly
- Real-time calculations match desktop logic precisely
- Professional proposals enhanced with AI generation

## Development URLs
- Frontend: http://localhost:7000
- Backend API: http://localhost:8000
- Full Application: http://localhost:80
- Database: localhost:5432

## Company Information
- Capitol Engineering Company
- 724 E Southern Pacific Dr, Phoenix AZ 85034
- Phone: 602-281-6517 | Mobile: 951-732-1514
- Website: www.capitolaz.com