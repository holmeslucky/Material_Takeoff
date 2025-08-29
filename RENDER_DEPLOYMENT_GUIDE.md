# Render Deployment Guide - Capitol Takeoff

## 🚀 Quick Deploy to Render (FREE)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 3: Deploy from Dashboard
1. Click "New +" → "Blueprint"
2. Connect your `capitol-takeoff` repository
3. Render will auto-detect the `render.yaml` file
4. Click "Apply" to deploy

### Step 4: Set Environment Variables
In Render dashboard, set these **REQUIRED** variables:

```bash
OPENAI_API_KEY=sk-proj-your-openai-key-here
```

**Optional Variables (already configured in render.yaml):**
- COMPANY_NAME=Indolent Designs  
- COMPANY_CONTACT=Blake Holmes
- COMPANY_EMAIL=indolentforge@gmail.com
- JWT_SECRET=auto-generated

### Step 5: Access Your Site
- Your app will be live at: `https://your-app-name.onrender.com`
- Database included automatically (PostgreSQL)
- SSL/HTTPS automatic
- Auto-deployments on git push

## 🎯 What You Get FREE
- ✅ Web hosting
- ✅ PostgreSQL database  
- ✅ SSL certificate
- ✅ Custom domain support
- ✅ Auto git deployments
- ✅ 750 hours/month (enough for 24/7)

## 🔧 Configuration Highlights

### Build Process
1. Install frontend dependencies (`npm install`)
2. Build React frontend (`npm run build`)
3. Copy frontend files to backend/static
4. Install Python dependencies (`pip install -r requirements.txt`)
5. Start FastAPI server

### Database
- Automatic PostgreSQL database creation
- Connection string auto-injected as `DATABASE_URL`
- Tables created automatically on startup

### Company Branding
- **Company:** Indolent Designs
- **Contact:** Blake Holmes
- **Email:** indolentforge@gmail.com
- **Phone:** 951-732-1514

## 🔍 Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Ensure Node.js version compatibility

### Database Issues  
- Render provides PostgreSQL automatically
- Connection string is auto-injected
- Tables are created on first startup

### Frontend Not Loading
- Verify build completed successfully
- Check static file serving in logs
- Ensure React build files are in `/static`

## 🔄 Updates & Maintenance
- **Automatic deploys:** Push to `main` branch = auto deploy
- **Database persists:** Data survives deployments  
- **Logs available:** Real-time in Render dashboard
- **Zero downtime:** Rolling deployments

## 📱 After Deployment
1. Test all functionality
2. Verify database connectivity
3. Check material search/pricing
4. Test proposal generation
5. Confirm OpenAI integration works

## 🆘 Support
- Render Docs: https://render.com/docs
- This deployment is optimized for the FREE tier
- Upgrade available if more resources needed

---

**Your app will be live in ~5-10 minutes after clicking deploy!** 🎉