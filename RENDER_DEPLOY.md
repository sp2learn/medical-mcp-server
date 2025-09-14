# 🚀 Deploy Medical MCP Server to Render

## Quick Deployment Steps

### 1. **Push to GitHub**
```bash
# Initialize git repo (if not already done)
git init
git add .
git commit -m "Medical MCP Server with authentication"

# Push to GitHub
git remote add origin https://github.com/yourusername/medical-mcp-server.git
git push -u origin main
```

### 2. **Deploy on Render**

1. **Go to:** https://render.com
2. **Sign up/Login** with GitHub
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repo:** `medical-mcp-server`
5. **Configure:**
   - **Name:** `medical-mcp-server`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python web_app.py`

### 3. **Set Environment Variables**

In Render dashboard, add these environment variables:

- **MEDICAL_MODEL:** `gemini`
- **GOOGLE_API_KEY:** `your_actual_gemini_api_key_here`

### 4. **Deploy!**

Click **"Create Web Service"** and Render will:
- ✅ Build your app
- ✅ Deploy to a public URL
- ✅ Provide HTTPS automatically
- ✅ Monitor health checks

## 🌐 **Your App Will Be Live At:**
`https://medical-mcp-server-xyz.onrender.com`

## 🔐 **Demo Accounts:**
- **demo** / password
- **doctor** / secret123  
- **admin** / admin2024

## 📋 **Features:**
- ✅ User authentication
- ✅ Medical Q&A with Gemini
- ✅ Symptom checker
- ✅ Professional medical disclaimers
- ✅ Mobile responsive design
- ✅ Session management

## 🔧 **Troubleshooting:**

**If deployment fails:**
1. Check build logs in Render dashboard
2. Verify environment variables are set
3. Ensure `requirements.txt` is complete
4. Check that `GOOGLE_API_KEY` is valid

**If app doesn't start:**
1. Check service logs
2. Verify port configuration
3. Test health check endpoint: `/health`