# Deployment Guide

This guide covers deploying your AI Travel Planner with Vercel (frontend) and Render (backend).

## Architecture

- **Frontend**: Next.js app deployed on Vercel
- **Backend**: Flask API deployed on Render
- **Database**: PostgreSQL (Supabase or Render PostgreSQL)

---

## Backend Deployment (Render)

### 1. Prerequisites
- Push your code to GitHub
- Create a [Render](https://render.com) account

### 2. Create Web Service on Render

1. Go to Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `ai-travel-planner-backend` (or your choice)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
DATABASE_URL=<your-postgresql-connection-string>
JWT_SECRET_KEY=<generate-secure-random-string>
FRONTEND_URLS=https://your-app.vercel.app
GOOGLE_CLIENT_ID=<your-google-oauth-client-id>
OPENAI_API_KEY=<your-openai-api-key>
```

**Important**: 
- Make sure there are NO trailing spaces or newlines in `DATABASE_URL`
- Generate a secure `JWT_SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
- Use comma-separated list for multiple frontend URLs

### 4. Database Setup

**Option A: Render PostgreSQL**
1. Create a PostgreSQL database on Render
2. Copy the **Internal Database URL** to `DATABASE_URL`

**Option B: Supabase PostgreSQL**
1. Create a project on [Supabase](https://supabase.com)
2. Go to Project Settings → Database → Connection String
3. Copy the connection string to `DATABASE_URL`

### 5. Deploy

- Click **Create Web Service**
- Render will automatically deploy
- Your backend URL: `https://your-backend-name.onrender.com`

### 6. Test Backend

```bash
curl https://your-backend-name.onrender.com/health
```

Should return: `{"status":"healthy","database":"connected"}`

---

## Frontend Deployment (Vercel)

### 1. Prerequisites
- Push your code to GitHub
- Create a [Vercel](https://vercel.com) account

### 2. Import Project

1. Go to Vercel Dashboard → **Add New** → **Project**
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Set Environment Variables

In Vercel project settings → **Environment Variables**, add:

```
NEXT_PUBLIC_API_URL=https://your-backend-name.onrender.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<your-google-oauth-client-id>
```

**Important**: 
- Must use your **actual Render backend URL**
- Google Client ID must match backend

### 4. Deploy

- Click **Deploy**
- Vercel will build and deploy automatically
- Your frontend URL: `https://your-app.vercel.app`

### 5. Update Backend CORS

Go back to Render and update `FRONTEND_URLS`:

```
FRONTEND_URLS=https://your-app.vercel.app
```

If you have a custom domain, add it:
```
FRONTEND_URLS=https://your-app.vercel.app,https://yourdomain.com
```

---

## Google OAuth Setup (Optional)

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth Client ID**
5. Application type: **Web application**
6. Add authorized JavaScript origins:
   - `http://localhost:3000` (for development)
   - `https://your-app.vercel.app` (for production)
7. Add authorized redirect URIs:
   - `http://localhost:3000` (for development)
   - `https://your-app.vercel.app` (for production)

### 2. Configure Environment Variables

Copy the **Client ID** and add it to both:
- Vercel: `NEXT_PUBLIC_GOOGLE_CLIENT_ID`
- Render: `GOOGLE_CLIENT_ID`

---

## Post-Deployment Checklist

### Backend (Render)
- [ ] Backend is accessible at `/health` endpoint
- [ ] Database connection is working
- [ ] CORS allows your frontend URL
- [ ] Environment variables have no trailing whitespace

### Frontend (Vercel)
- [ ] Frontend loads successfully
- [ ] API calls reach backend (check browser network tab)
- [ ] Authentication works
- [ ] Trip planning works
- [ ] Saved trips feature works

### Testing
1. **Sign up** for a new account
2. **Plan a trip** to any destination
3. **Save the trip** (should appear in "Saved Trips")
4. **View saved trips** from user menu
5. **Test all features**: itinerary, budget, bookings, map, weather, news

---

## Troubleshooting

### "Failed to fetch" errors
- Check `NEXT_PUBLIC_API_URL` in Vercel matches your Render backend URL
- Check browser console for CORS errors
- Verify `FRONTEND_URLS` in Render includes your Vercel URL

### Database connection errors
- Check `DATABASE_URL` has no trailing whitespace
- Verify database credentials are correct
- Check if database is accessible (Render PostgreSQL uses internal URLs)

### Authentication not working
- Verify `JWT_SECRET_KEY` is set in backend
- Check that frontend sends `Authorization` header
- Verify token is stored in localStorage

### Google OAuth not working
- Check `GOOGLE_CLIENT_ID` matches in both frontend and backend
- Verify authorized origins include your Vercel URL
- Check Google Cloud Console for error messages

---

## Monitoring

### Render
- View logs: Dashboard → Your Service → Logs
- View metrics: Dashboard → Your Service → Metrics
- Set up alerts for errors

### Vercel
- View deployments: Dashboard → Your Project → Deployments
- View logs: Click on a deployment → View Function Logs
- View analytics: Dashboard → Your Project → Analytics

---

## Updating Your App

### Frontend Updates
```bash
git add .
git commit -m "Update frontend"
git push
```
Vercel will automatically redeploy.

### Backend Updates
```bash
git add .
git commit -m "Update backend"
git push
```
Render will automatically redeploy.

---

## Cost Optimization

### Free Tier Limits
- **Vercel**: 100 GB bandwidth/month, unlimited static sites
- **Render**: Free tier spins down after 15 minutes of inactivity
- **Supabase**: 500 MB database, 2 GB bandwidth/month

### Keeping Render Active
Render's free tier spins down. To prevent this:
1. Use a paid plan ($7/month keeps it always on)
2. Or accept 30-60 second cold starts on first request

---

## Security Best Practices

1. **Never commit** `.env` files to git
2. **Rotate secrets** regularly (JWT_SECRET_KEY, API keys)
3. **Use HTTPS** only in production
4. **Set short JWT expiration** (currently 1 hour)
5. **Monitor logs** for suspicious activity
6. **Keep dependencies updated** regularly

---

## Support

If you encounter issues:
1. Check Render logs for backend errors
2. Check Vercel function logs for frontend errors
3. Check browser console for client-side errors
4. Verify all environment variables are set correctly
