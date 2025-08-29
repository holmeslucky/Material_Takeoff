# Railway Production Deployment Guide

## 🚨 PRE-DEPLOYMENT SECURITY CHECKLIST

### ✅ COMPLETED SECURITY FIXES:
- [x] OpenAI API key removed from all files (must be set in Railway environment variables)
- [x] Hardcoded localhost URLs replaced with dynamic configuration
- [x] Production JWT secret configured (must be set in Railway environment variables)
- [x] CORS origins configured for production
- [x] .env files added to .gitignore
- [x] PostgreSQL database configuration ready
- [x] Frontend sourcemaps disabled for production
- [x] Debug console.log statements removed from critical components
- [x] Error handling improved to prevent information leakage

## 🔐 REQUIRED RAILWAY ENVIRONMENT VARIABLES

### Critical Security Variables (SET THESE FIRST):
```bash
OPENAI_API_KEY=sk-proj-your-existing-api-key-here
JWT_SECRET=generate-a-strong-random-string-here
DATABASE_URL=postgresql://postgres:password@railway.app:5432/railway
```

### Application Configuration:
```bash
ENVIRONMENT=production
COMPANY_NAME=Capitol Engineering Company
COMPANY_ADDRESS=724 E Southern Pacific Dr, Phoenix AZ 85034
COMPANY_PHONE=602-281-6517
COMPANY_MOBILE=951-732-1514
COMPANY_WEBSITE=www.capitolaz.com
OPENAI_MODEL=gpt-4o-mini
CORS_ORIGINS=*
LOG_LEVEL=INFO
```

## 🚀 RAILWAY DEPLOYMENT STEPS

### 1. Connect Repository to Railway
1. Go to Railway.app dashboard
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository: `capitol-takeoff`

### 2. Configure Services
Railway will automatically detect and create:
- **Web Service**: Backend API (Python/FastAPI)
- **Database**: PostgreSQL database

### 3. Set Environment Variables
In Railway dashboard → Settings → Environment:
1. Add all variables from the list above
2. **CRITICAL**: Use your actual OpenAI API key
3. **CRITICAL**: Generate a strong JWT secret (32+ random characters)

### 4. Database Setup
Railway will automatically:
- Create PostgreSQL database
- Set DATABASE_URL environment variable
- Tables will be created automatically on first startup

### 5. Domain Configuration
After deployment:
1. Railway provides a domain: `your-app-name.railway.app`
2. Update CORS settings if needed
3. Test all functionality

## 🧪 POST-DEPLOYMENT TESTING

### Health Checks:
- [ ] Health endpoint: `https://your-app.railway.app/health`
- [ ] API root: `https://your-app.railway.app/`
- [ ] Frontend loads: `https://your-app.railway.app/projects`

### Functionality Tests:
- [ ] Create new project
- [ ] Add takeoff items
- [ ] Save project data
- [ ] Material search works
- [ ] Calculations are accurate
- [ ] No console errors in browser

### Security Validation:
- [ ] No API keys visible in browser network tab
- [ ] Error messages don't leak sensitive information
- [ ] HTTPS is enforced
- [ ] Database connections are secure

## 🔧 TROUBLESHOOTING

### Common Issues:

1. **Database Connection Failed**
   - Check DATABASE_URL in Railway environment variables
   - Verify PostgreSQL service is running

2. **OpenAI API Errors**
   - Verify OPENAI_API_KEY is set correctly in Railway
   - Check API key has sufficient credits

3. **Frontend API Errors**
   - Check CORS_ORIGINS setting
   - Verify all hardcoded URLs are replaced

4. **Build Failures**
   - Check nixpacks.toml configuration
   - Verify all dependencies in requirements.txt

## 📊 MONITORING

### Railway Provides:
- Application logs
- Resource usage metrics
- Deployment history
- Database connection stats

### Recommended Monitoring:
- Set up Railway deployment notifications
- Monitor error rates in logs
- Track database performance
- Monitor OpenAI API usage

## 🔄 MAINTENANCE

### Regular Tasks:
1. Monitor logs for errors
2. Check database size and performance
3. Monitor OpenAI API usage/costs
4. Update dependencies as needed
5. Backup critical project data

### Updates:
- Railway automatically deploys on git push to main branch
- Database migrations will run automatically
- Zero-downtime deployments

---

## ⚠️ IMPORTANT NOTES

1. **Never commit API keys** - Always use Railway environment variables
2. **Database is persistent** - Data will survive deployments
3. **Logs are retained** - Monitor for sensitive information
4. **HTTPS is automatic** - Railway provides SSL certificates
5. **Scaling is available** - Can upgrade resources as needed

## 🆘 SUPPORT

- Railway Documentation: https://docs.railway.app/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- PostgreSQL on Railway: https://docs.railway.app/databases/postgresql