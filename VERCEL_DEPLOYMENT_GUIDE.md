# Vercel Deployment Guide - Capitol Takeoff

## 🚀 Quick Deploy to Vercel (FREE)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### Step 2: Deploy to Vercel
1. Go to **[vercel.com](https://vercel.com)**
2. Click **"Sign up"** → **"Continue with GitHub"**
3. Click **"Import Project"**
4. Select your **`holmeslucky/Takeoff`** repository
5. Click **"Deploy"**

### Step 3: Set Environment Variables
In Vercel dashboard → Settings → Environment Variables, add:

```bash
OPENAI_API_KEY=sk-proj-your-openai-key-here
JWT_SECRET=your-jwt-secret-here
DATABASE_URL=your-database-url-here
```

### Step 4: Database Options

**Option A: Use Vercel Postgres (Recommended)**
1. In Vercel dashboard → Storage → Create Database
2. Choose **"Postgres"**
3. Vercel will auto-set `DATABASE_URL`

**Option B: Use Supabase (Free)**
1. Go to [supabase.com](https://supabase.com) → New Project
2. Get connection string from Settings → Database
3. Add as `DATABASE_URL` in Vercel

**Option C: Use PlanetScale (Free)**
1. Go to [planetscale.com](https://planetscale.com) → New Database
2. Get connection string from overview
3. Add as `DATABASE_URL` in Vercel

## 🎯 What You Get FREE
- ✅ **Frontend hosting** (unlimited)
- ✅ **Serverless API functions** (100GB-hours/month)
- ✅ **SSL certificate** (automatic)
- ✅ **Custom domain support**
- ✅ **Auto git deployments**
- ✅ **Edge network** (global CDN)

## 🔧 How It Works

### Frontend (React)
- Builds automatically with `npm run build`
- Served from Vercel's global CDN
- Lightning fast loading

### Backend (FastAPI)
- Runs as serverless functions
- Auto-scales on demand
- `/api/*` routes handled by Python

### Database
- PostgreSQL via Vercel Postgres or Supabase
- Connection pooling included
- Automatic backups

## 📱 After Deployment

Your app will be live at: `https://your-app-name.vercel.app`

### Test Checklist:
1. ✅ Frontend loads correctly
2. ✅ API endpoints work (`/api/v1/projects`)
3. ✅ Database connectivity
4. ✅ Material search functions
5. ✅ Proposal generation works
6. ✅ OpenAI integration active

## 🔄 Updates & Maintenance

- **Auto-deploys:** Push to `main` = instant deploy
- **Preview deploys:** Every PR gets preview URL
- **Rollbacks:** One-click rollback to previous versions
- **Analytics:** Built-in performance monitoring

## 🆘 Troubleshooting

### Build Fails
- Check Node.js version in Vercel settings
- Verify all dependencies in package.json

### API Errors
- Check serverless function logs in Vercel dashboard
- Verify environment variables are set

### Database Issues
- Ensure DATABASE_URL is properly formatted
- Check connection limits (serverless functions)

## 💡 Pro Tips

1. **Custom Domain:** Add your own domain in Vercel settings
2. **Performance:** Vercel automatically optimizes images and assets
3. **Monitoring:** Built-in Web Vitals and performance metrics
4. **Collaboration:** Invite team members to manage deployments

---

**Deployment time:** ~2-3 minutes after clicking deploy! 🎉

**Your steel takeoff system will be live worldwide with enterprise-grade performance!**