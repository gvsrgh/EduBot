# Deployment Guide

## Deploying to Vercel (Frontend)

### Prerequisites
- GitHub account
- Vercel account
- Backend API deployed and accessible

### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Production ready deployment"
   git push origin master
   ```

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Select the repository

3. **Configure Project**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

4. **Add Environment Variables**
   
   In Vercel project settings → Environment Variables, add:
   
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com/api
   ```
   
   Replace `your-backend-url.com` with your actual backend API URL.

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your frontend is now live!

### Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

---

## Deploying Backend

### Option 1: Railway

1. **Create Account**
   - Sign up at https://railway.app

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository

3. **Configure Service**
   - Root Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   ```
   DATABASE_URL=postgresql://... (Railway provides this)
   DATABASE_URL_SYNC=postgresql://...
   JWT_SECRET_KEY=<generate-strong-secret>
   OPENAI_API_KEY=<your-key>
   GOOGLE_API_KEY=<your-key>
   CORS_ORIGINS=https://your-frontend.vercel.app
   DEBUG=False
   ```

5. **Add PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway automatically sets DATABASE_URL

6. **Deploy**
   - Railway automatically deploys on push
   - Note your backend URL for frontend env variable

### Option 2: Render

1. **Create Account**
   - Sign up at https://render.com

2. **Create Web Service**
   - New → Web Service
   - Connect your repository
   - Root Directory: `backend`

3. **Configure**
   - Name: edubot-backend
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt && alembic upgrade head`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add PostgreSQL Database**
   - New → PostgreSQL
   - Note the Internal Database URL

5. **Add Environment Variables**
   Same as Railway above

### Option 3: Docker Deployment

For any platform supporting Docker (DigitalOcean, AWS, GCP):

1. **Build Docker image**
   ```bash
   cd backend
   docker build -t edubot-backend .
   ```

2. **Push to registry**
   ```bash
   docker tag edubot-backend your-registry/edubot-backend
   docker push your-registry/edubot-backend
   ```

3. **Deploy with environment variables**

---

## Database Setup

### PostgreSQL

For production, use a managed PostgreSQL service:
- **Railway**: Automatic PostgreSQL
- **Render**: Built-in PostgreSQL
- **Supabase**: Free tier available
- **AWS RDS**: Production-grade
- **Neon**: Serverless PostgreSQL

### Migrations

After deployment, run migrations:
```bash
alembic upgrade head
```

### Initial Admin User

Create an admin user with @pvpsiddhartha.ac.in email via the registration page.

---

## Vector Database (Qdrant)

### Option 1: Qdrant Cloud (Recommended)

1. Sign up at https://cloud.qdrant.io
2. Create a cluster
3. Get API key and URL
4. Set `QDRANT_URL` environment variable

### Option 2: Self-hosted

Deploy Qdrant using Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

---

## Environment Variables Checklist

### Frontend
- ✅ `NEXT_PUBLIC_API_URL`

### Backend
- ✅ `DATABASE_URL`
- ✅ `DATABASE_URL_SYNC`
- ✅ `JWT_SECRET_KEY` (use strong random string)
- ✅ `OPENAI_API_KEY` (optional)
- ✅ `GOOGLE_API_KEY` (optional)
- ✅ `OLLAMA_BASE_URL` (optional)
- ✅ `QDRANT_URL`
- ✅ `CORS_ORIGINS` (your frontend URL)
- ✅ `DEBUG=False`

---

## Post-Deployment

1. **Test the application**
   - Register a new user
   - Test chat functionality
   - Test all AI providers
   - Verify admin settings (if admin user)

2. **Monitor logs**
   - Check for errors
   - Monitor API performance
   - Track database queries

3. **Set up monitoring** (Optional)
   - Sentry for error tracking
   - Vercel Analytics
   - Railway/Render metrics

---

## Troubleshooting

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify CORS settings in backend
- Check backend is running

### Database connection errors
- Verify `DATABASE_URL` is correct
- Check database is running
- Run migrations: `alembic upgrade head`

### AI providers not working
- Verify API keys are set
- Test connection from backend logs
- Check provider-specific rate limits

---

## Security Checklist

- ✅ Use strong `JWT_SECRET_KEY`
- ✅ Set `DEBUG=False` in production
- ✅ Use HTTPS for both frontend and backend
- ✅ Configure proper CORS origins
- ✅ Keep API keys secure (use environment variables)
- ✅ Regular security updates
- ✅ Monitor for suspicious activity

---

## Scaling Considerations

1. **Database**: Use connection pooling
2. **Backend**: Horizontal scaling with load balancer
3. **Cache**: Add Redis for session management
4. **CDN**: Use Vercel's CDN for frontend assets
5. **Rate limiting**: Implement API rate limits

---

## Support

For deployment issues, check:
- Vercel documentation: https://vercel.com/docs
- Railway documentation: https://docs.railway.app
- Render documentation: https://render.com/docs
