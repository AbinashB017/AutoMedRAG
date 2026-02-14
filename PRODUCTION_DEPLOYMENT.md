# 🚀 Full Production Deployment Guide

## Backend Deployment (Render.com)

### Prerequisites
- GitHub account (already have it)
- Render.com account (free)

### Step-by-Step

1. **Create Render Account**
   - Visit: https://render.com
   - Sign up with GitHub
   - Authorize repository access

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Select `AbinashB017/AutoMedRAG` repository
   - Fill form:
     ```
     Name: automedrag-backend
     Runtime: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
     Plan: Free
     ```
   - Click "Create Web Service"

3. **Wait for Deployment**
   - Check status in dashboard
   - Takes 2-3 minutes
   - Look for: "Your service is live"

4. **Get Backend URL**
   - Example: `https://automedrag-backend.onrender.com`
   - Save this URL - you'll need it for Streamlit

---

## Frontend Deployment (Streamlit Cloud)

### Prerequisites
- GitHub account (already have it)
- Streamlit.io account (sign up with GitHub)

### Step-by-Step

1. **Go to Streamlit Cloud**
   - https://share.streamlit.io
   - Sign in with GitHub

2. **Deploy New App**
   - Click "New app"
   - Select:
     ```
     Repository: AbinashB017/AutoMedRAG
     Branch: main
     Main file: streamlit_app.py
     ```
   - Click "Deploy"

3. **Add Backend URL**
   - Wait for app to deploy (2-3 minutes)
   - Click Settings (⚙️ icon, top right)
   - Go to "Secrets" tab
   - Add:
     ```toml
     API_URL = "https://automedrag-backend.onrender.com"
     ```
     *(Replace with your Render URL from Step 1)*
   - Click "Save"
   - App auto-redeploys

4. **Get Frontend URL**
   - Now visible at top of page
   - Example: `https://automedrag-abinashb017.streamlit.app`

---

## Testing Deployment

### Test 1: Check Backend API
```
URL: https://automedrag-backend.onrender.com/
Expected: {"message": "AutoMedRAG API is running", ...}
Status: 200 OK
```

### Test 2: Check API Docs
```
URL: https://automedrag-backend.onrender.com/docs
Expected: Swagger UI interface
```

### Test 3: Test from Frontend
1. Open your Streamlit URL
2. Enter: "What is pneumonia?"
3. Click "Search"
4. Should see results in 2-3 seconds
5. Check sidebar: Should show ✅ Backend Connected

---

## Production Checklist

- [ ] Backend deployed on Render
- [ ] Backend URL obtained
- [ ] Frontend deployed on Streamlit Cloud
- [ ] Backend URL added to Streamlit secrets
- [ ] Frontend tested with backend
- [ ] Query test successful
- [ ] Share URLs with others

---

## Important Notes

### Free Tier Limitations
- **Render**: Spins down after 15 mins of inactivity
  - First request after idle takes 30 seconds
  - Solution: Keep backend warm with requests or upgrade plan

- **Streamlit**: Fully free, always active
  - Can handle unlimited users on free tier

### Upgrading (Optional)
- **Render**: $7/month for always-on
- **Streamlit**: Free forever for public apps

---

## Troubleshooting

### Issue: Backend seems offline in Streamlit
**Solution**: 
- Wait 30 seconds (Render free tier spins up)
- Check Render dashboard
- Verify API_URL in Streamlit secrets is correct

### Issue: CORS errors
**Solution**: Not applicable - backend has CORS enabled

### Issue: Slow first request
**Solution**: Normal on free Render tier - add load-balancer or upgrade

### Issue: Can't see results
**Solution**:
- Check backend health at /
- Verify API_URL in secrets
- Check Streamlit logs (click "Manage app" → "View logs")

---

## URLs After Deployment

| Service | URL |
|---------|-----|
| GitHub Repo | https://github.com/AbinashB017/AutoMedRAG |
| Backend API | https://automedrag-backend.onrender.com |
| API Docs | https://automedrag-backend.onrender.com/docs |
| Frontend | https://automedrag-[username].streamlit.app |

---

## Share with Others

After deployment, share:
```
Frontend: https://automedrag-[username].streamlit.app
(No backend URL needed - it's configured in secrets)
```

---

## Support

If issues occur:
1. Check Render dashboard for backend status
2. Check Streamlit Cloud logs
3. Verify API_URL in Streamlit secrets
4. Test backend directly: curl https://automedrag-backend.onrender.com/

Good luck! 🚀
