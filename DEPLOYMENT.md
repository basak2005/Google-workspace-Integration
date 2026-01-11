# 🚀 Vercel Deployment Guide

This guide walks you through deploying the Google Services app to Vercel with MongoDB Atlas.

## 📋 Prerequisites

1. [Vercel Account](https://vercel.com/signup)
2. [MongoDB Atlas Account](https://www.mongodb.com/cloud/atlas/register) (Free tier available)
3. [Google Cloud Console](https://console.cloud.google.com/) project with OAuth configured

---

## 🗄️ Step 1: Set Up MongoDB Atlas (Free Tier)

### 1.1 Create a Cluster

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Click **"Build a Database"**
3. Select **"M0 FREE"** tier
4. Choose your cloud provider and region (closest to your users)
5. Click **"Create"**

### 1.2 Create Database User

1. Go to **Database Access** in the left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Enter username and generate a secure password
5. Set privileges to **"Read and write to any database"**
6. Click **"Add User"**

### 1.3 Configure Network Access

1. Go to **Network Access** in the left sidebar
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (0.0.0.0/0) for Vercel serverless
   - ⚠️ For production, consider using [Vercel's IP ranges](https://vercel.com/guides/how-to-allowlist-deployment-ip-address)
4. Click **"Confirm"**

### 1.4 Get Connection String

1. Go to **Database** in the left sidebar
2. Click **"Connect"** on your cluster
3. Select **"Connect your application"**
4. Copy the connection string (looks like):
   ```
   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your database user password
6. Add database name: `mongodb+srv://...mongodb.net/google_services?retryWrites=true&w=majority`

---

## 🔧 Step 2: Update Google OAuth Settings

### 2.1 Add Authorized Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Under **Authorized redirect URIs**, add:
   ```
   https://your-backend-name.vercel.app/auth/callback
   ```
6. Under **Authorized JavaScript origins**, add:
   ```
   https://your-frontend-name.vercel.app
   https://your-backend-name.vercel.app
   ```
7. Click **Save**

---

## 🖥️ Step 3: Deploy Backend to Vercel

### 3.1 Deploy via Vercel CLI

```bash
cd Backend
npm i -g vercel  # Install Vercel CLI if not installed
vercel login
vercel
```

### 3.2 Or Deploy via GitHub

1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click **"Add New..."** → **"Project"**
4. Import your GitHub repository
5. Set **Root Directory** to `Backend`
6. Click **"Deploy"**

### 3.3 Set Backend Environment Variables

In Vercel Dashboard → Your Backend Project → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `GOOGLE_CLIENT_ID` | Your Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth Client Secret |
| `GOOGLE_MAPS_API_KEY` | Your Google Maps API Key |
| `GEMINI_API_KEY` | Your Gemini API Key |
| `MONGODB_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/google_services?retryWrites=true&w=majority` |
| `DATABASE_NAME` | `google_services` |
| `BACKEND_URL` | `https://your-backend.vercel.app` |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` |

After adding variables, redeploy: **Deployments** → **...** → **Redeploy**

---

## 🎨 Step 4: Deploy Frontend to Vercel

### 4.1 Deploy via Vercel CLI

```bash
cd Frontend
vercel
```

### 4.2 Or Deploy via GitHub

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import the same repository
4. Set **Root Directory** to `Frontend`
5. Framework Preset should auto-detect **Vite**
6. Click **"Deploy"**

### 4.3 Set Frontend Environment Variables

In Vercel Dashboard → Your Frontend Project → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://your-backend.vercel.app` |

After adding variables, redeploy.

---

## ✅ Step 5: Final Verification

### 5.1 Update Google OAuth Redirect URIs

Now that you have your actual Vercel URLs, update Google Cloud Console:

1. **Authorized redirect URIs**: 
   - `https://your-actual-backend.vercel.app/auth/callback`
   
2. **Authorized JavaScript origins**:
   - `https://your-actual-frontend.vercel.app`
   - `https://your-actual-backend.vercel.app`

### 5.2 Test the Deployment

1. Visit your frontend URL: `https://your-frontend.vercel.app`
2. Click Login/Connect with Google
3. Complete OAuth flow
4. Verify you can access Google services

---

## 🔄 Environment Variables Summary

### Backend (.env / Vercel)
```env
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_MAPS_API_KEY=xxx
GEMINI_API_KEY=xxx
MONGODB_URI=mongodb+srv://...
DATABASE_NAME=google_services
BACKEND_URL=https://your-backend.vercel.app
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend (.env / Vercel)
```env
VITE_API_URL=https://your-backend.vercel.app
```

---

## 🐛 Troubleshooting

### CORS Errors
- Ensure `FRONTEND_URL` is set correctly in backend
- Check that the URL doesn't have a trailing slash

### OAuth Redirect Mismatch
- Ensure the redirect URI in Google Console **exactly** matches `BACKEND_URL/auth/callback`
- URLs are case-sensitive

### MongoDB Connection Issues
- Verify the connection string is correct
- Check that Network Access allows `0.0.0.0/0`
- Ensure password is URL-encoded if it contains special characters

### Cold Start Delays
- First request after inactivity may be slow (serverless cold start)
- This is normal for free tier

---

## 📊 MongoDB Atlas Free Tier Limits

- **Storage**: 512 MB
- **RAM**: Shared
- **Connections**: 500 max
- **Data Transfer**: 10 GB/month

This is sufficient for personal projects and development.

---

## 🔐 Security Notes

1. Never commit `.env` files to git
2. Use strong, unique passwords for MongoDB
3. Consider restricting IP access for production
4. Regularly rotate API keys and secrets
5. Enable 2FA on all accounts

---

## 📝 Local Development

For local development, create `.env` files:

**Backend/.env**
```env
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_MAPS_API_KEY=xxx
GEMINI_API_KEY=xxx
MONGODB_URI=mongodb+srv://...
DATABASE_NAME=google_services
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

**Frontend/.env**
```env
VITE_API_URL=http://localhost:8000
```

Run locally:
```bash
# Terminal 1 - Backend
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 - Frontend
cd Frontend
npm install
npm run dev
```
