# 🚀 GitHub & Streamlit Cloud Deployment Guide

## Step 1: Push to GitHub

### Create a GitHub Repository

1. Go to [GitHub.com](https://github.com/new)
2. Create new repository named `automedrag`
3. Choose "Public" (for Streamlit Cloud free tier)
4. Copy the repository URL

### Initialize Git & Push

```bash
cd d:\automedrag

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AutoMedRAG - Medical Q&A System"

# Add remote repository (replace with your GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/automedrag.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend (Choose One)

### Option A: Deploy Backend to Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `automedrag-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - **Environment Variables**:
     ```
     NVIDIA_API_KEY=your_key_here (optional)
     ```
5. Click "Create Web Service"
6. Note the deployed URL (e.g., `https://automedrag-backend.onrender.com`)

### Option B: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables
5. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
6. Copy the deployed URL

### Option C: Deploy Backend to Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create automedrag-backend

# Set environment variables
heroku config:set NVIDIA_API_KEY=your_key_here -a automedrag-backend

# Create Procfile (if not exists)
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port 8000" > Procfile

# Push to Heroku
git push heroku main
```

---

## Step 3: Deploy Frontend to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New App"
3. Connect your GitHub account
4. Select:
   - **Repository**: `YOUR_USERNAME/automedrag`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click "Deploy"
6. Go to Settings (gear icon)
7. Add Secrets:
   ```toml
   API_URL = "https://automedrag-backend.onrender.com"
   # (Use your actual backend URL)
   ```
8. Click "Save" and app will redeploy automatically

---

## Project Structure for Deployment

```
automedrag/
├── streamlit_app.py          ← Main Streamlit Cloud entry point
├── requirements.txt          ← All dependencies
├── .streamlit/
│   ├── config.toml          ← Streamlit configuration
│   └── secrets.toml         ← Local secrets (git ignored)
├── backend/
│   ├── main.py
│   ├── services/
│   ├── models/
│   └── utils/
├── frontend/
│   └── app.py
├── .gitignore
├── .env.example
├── Procfile                  ← For Heroku deployment
└── README.md
```

---

## Environment Variables Needed

### Backend (.env file)
```
NVIDIA_API_KEY=your_key_here  # Optional - for LLM features
NVIDIA_MODEL=meta/llama3-70b-instruct
PUBMED_MAX_RESULTS=20
```

### Streamlit Cloud (Settings → Secrets)
```toml
API_URL = "https://your-backend-url.com"
```

---

## Quick Deployment Commands

### Local Testing
```bash
# Terminal 1: Start Backend
uvicorn backend.main:app --reload

# Terminal 2: Start Frontend
streamlit run streamlit_app.py
```

### Deploy All
```bash
# 1. Push to GitHub
git add .
git commit -m "Update: [your message]"
git push

# 2. Streamlit Cloud auto-redeploys on push
# 3. Backend redeploys if using Render/Railway with auto-deploy

# 3. Monitor deployment
# - Streamlit Cloud: Check deploy logs
# - Render: Check deploys tab
```

---

## Troubleshooting Deployment

### Issue: Backend Connection Failed
**Solution**: 
- Verify backend URL in Streamlit secrets
- Check backend is actually deployed and running
- Add `/` endpoint test

### Issue: CORS Error
**Solution**: Backend has CORS enabled - should work. Check:
- Backend is running
- API_URL in secrets is correct (with https://)

### Issue: Slow Response
**Solution**:
- Backend might be on free tier (sleeps after inactivity)
- Consider upgrading tier or using paid deployment

### Issue: Missing Dependencies
**Solution**: Make sure `requirements.txt` has all packages

---

## Production Checklist

- [ ] GitHub repository created and pushed
- [ ] Backend deployed (Render/Railway/Heroku)
- [ ] Frontend deployed to Streamlit Cloud
- [ ] Secrets configured in Streamlit Cloud
- [ ] Backend URL set in Streamlit secrets
- [ ] Test frontend connects to backend
- [ ] Test query works end-to-end
- [ ] Monitor logs for errors

---

## Useful Links

- **Streamlit Cloud Docs**: https://docs.streamlit.io/deploy/streamlit-cloud
- **Render Deployment**: https://render.com/docs
- **Railway Deployment**: https://railway.app/docs
- **Heroku Deployment**: https://devcenter.heroku.com

---

## Support

If you encounter issues:
1. Check backend logs
2. Check Streamlit Cloud deploy logs
3. Verify API URL in secrets
4. Test backend directly: `curl https://your-backend-url.com/`

---

**Ready to deploy? Follow the steps above!** 🚀
