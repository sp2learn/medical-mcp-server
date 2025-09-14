# Medical Query Web App - Deployment Guide

## 🚀 Quick Local Deployment

### Option 1: Direct Python
```bash
# Install web dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run the web app
python web_app.py
```
Visit: http://localhost:8000

### Option 2: Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```
Visit: http://localhost:8000

## ☁️ Cloud Deployment Options

### **No Docker Required (Platform manages everything)**

#### 1. Railway (Easiest - Runs on Railway's servers)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy (Railway handles Docker automatically)
railway login
railway init
railway up
```
**Where it runs:** Railway's cloud infrastructure
**Access:** Public URL provided by Railway

#### 2. Render (Runs on Render's servers)
1. Connect your GitHub repo to Render
2. Set environment variables: `GOOGLE_API_KEY`, `MEDICAL_MODEL=gemini`
3. Render automatically builds and runs your app
**Where it runs:** Render's cloud infrastructure
**Access:** Public URL like `https://your-app.onrender.com`

#### 3. Heroku (Runs on Heroku's servers)
```bash
# Create Procfile
echo "web: python web_app.py" > Procfile

# Deploy
heroku create your-medical-app
heroku config:set GOOGLE_API_KEY=your_key_here
heroku config:set MEDICAL_MODEL=gemini
git push heroku main
```
**Where it runs:** Heroku's cloud infrastructure
**Access:** Public URL like `https://your-medical-app.herokuapp.com`

### **Docker Container Services (You manage Docker)**

#### 4. AWS ECS (Docker runs on AWS)
```bash
# Build and push to AWS ECR
aws ecr create-repository --repository-name medical-app
docker build -t medical-app .
docker tag medical-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/medical-app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/medical-app:latest

# Deploy to ECS
aws ecs create-service --cluster default --service-name medical-app
```
**Where it runs:** AWS servers (EC2 instances)
**Access:** Public URL via AWS Load Balancer

#### 5. Google Cloud Run (Docker runs on Google Cloud)
```bash
# Deploy directly from source
gcloud run deploy medical-app --source . --platform managed --region us-central1
```
**Where it runs:** Google Cloud servers
**Access:** Public URL like `https://medical-app-xyz.a.run.app`

#### 6. Azure Container Instances (Docker runs on Azure)
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image medical-app .

# Deploy to Container Instances
az container create --resource-group myResourceGroup --name medical-app \
  --image myregistry.azurecr.io/medical-app:latest
```
**Where it runs:** Azure servers
**Access:** Public IP or custom domain

### **Local Development (Docker runs on your machine)**
```bash
# Runs on your local machine only
docker-compose up --build
```
**Where it runs:** Your local computer
**Access:** http://localhost:8000 (only you can access)

## 🔧 Environment Variables
- `GOOGLE_API_KEY`: Your Gemini API key
- `MEDICAL_MODEL`: Set to "gemini" or "nova"
- `AWS_ACCESS_KEY_ID`: (if using Nova)
- `AWS_SECRET_ACCESS_KEY`: (if using Nova)

## 🌐 Features
- Clean web interface
- Medical Q&A
- Symptom checker
- Mobile responsive
- Professional disclaimers
- Real-time responses