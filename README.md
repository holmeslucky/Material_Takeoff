# Capitol Takeoff - Professional Steel Estimating System

A modern web application for steel fabrication takeoffs and estimating, built for Capitol Engineering Company. Now live on Railway!

## Overview

Capitol Takeoff is a comprehensive steel estimating system that provides:
- Material Database Management - 1,918+ steel shapes with CWT pricing
- Project-based Takeoffs - 11-column takeoff grid matching industry standards  
- Automated Calculations - Real-time weight, length, and pricing calculations
- Professional Proposals - AI-enhanced proposal generation with OpenAI integration
- Company Branding - Fully customized for Capitol Engineering Company

## Architecture

### Backend (FastAPI)
- Python 3.11 with FastAPI framework
- PostgreSQL database with SQLAlchemy ORM
- Pydantic models for data validation
- Company Profile integration throughout

### Frontend (React)
- React 18 with TypeScript
- Tailwind CSS for responsive design
- Vite build system for optimal performance
- AG Grid for advanced data tables

### Infrastructure
- Docker containerized development
- Railway cloud deployment
- Nginx reverse proxy
- Redis caching (optional)

## Quick Start

### Development Environment

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd capitol-takeoff
   ```

2. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and settings
   ```

3. **Start Development (Windows)**
   ```bash
   ./dev-start.bat
   ```

3. **Start Development (Linux/Mac)**
   ```bash
   ./dev-start.sh
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Full App (Nginx): http://localhost:80

### Manual Development Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend  
npm install
npm run dev
```

## Development Status

### Phase 1: Foundation (Completed)
- Working backups of desktop application
- Database backup and migration preparation
- Feature baseline documentation

### Phase 2: Web Infrastructure (Completed)
- FastAPI backend with models, routers, services
- React frontend with TypeScript and Tailwind
- Docker development environment
- Railway deployment configuration

### Phase 3: Core Features (Completed)
- Material database migration (1,918+ materials)
- Takeoff entry system with 11-column grid
- Real-time calculations (weight, pricing, labor)
- Project management system
- Template system

### Phase 4: Production Ready (Pending)
- Railway deployment with CI/CD
- Database optimization
- Performance monitoring
- Security hardening
- User authentication

### Phase 5: AI Enhancement (Completed)
- OpenAI GPT-4o-mini integration
- AI-powered proposal generation
- Smart material suggestions
- Automated takeoff assistance

## Company Profile

Capitol Engineering Company
- Address: 724 E Southern Pacific Dr, Phoenix AZ 85034
- Phone: 602-281-6517
- Mobile: 951-732-1514  
- Website: www.capitolaz.com

## Configuration

### Environment Variables

```env
# Company Configuration
COMPANY_NAME=Capitol Engineering Company
COMPANY_ADDRESS=724 E Southern Pacific Dr, Phoenix AZ 85034
COMPANY_PHONE=602-281-6517
COMPANY_MOBILE=951-732-1514
COMPANY_WEBSITE=www.capitolaz.com

# OpenAI Integration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Development Commands

### Docker Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild services
docker-compose up --build

# Stop services
docker-compose down
```

### Backend Commands
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Commands  
```bash
cd frontend
npm install
npm run dev          # Development server
npm run build        # Production build  
npm run preview      # Preview build
```

## Deployment

### Railway Deployment
1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Manual Railway Deploy
```bash
railway login
railway up
```

## Project Structure

```
capitol-takeoff/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components  
│   │   └── styles/         # CSS styles
│   └── package.json
├── docker-compose.yml      # Development environment
└── railway.json           # Railway configuration
```

## Migration Status

Migrating from desktop CustomTkinter application to modern web stack while maintaining 100% feature parity.

Desktop Features Preserved:
- 11-column takeoff grid structure
- Material database with 1,918+ entries  
- CWT pricing calculations
- Auto/Manual labor modes
- Company branding and contact info
- Professional proposal generation

## Support

For technical support or questions:
- Contact: Capitol Engineering Company
- Phone: 602-281-6517
- Mobile: 951-732-1514

---

Capitol Takeoff - Professional Steel Estimating for the Modern Era