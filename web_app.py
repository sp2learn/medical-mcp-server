#!/usr/bin/env python3
"""
Medical Query Web App - Lightweight web interface for the medical MCP server
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv

from medical_client import MedicalClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Medical Query API", description="Medical information web service")

# Initialize medical client with error handling
try:
    medical_client = MedicalClient()
    print(f"✅ Medical client initialized with model: {medical_client.model_type}")
except Exception as e:
    print(f"❌ Failed to initialize medical client: {e}")
    medical_client = None

# Simple in-memory session store (use Redis/DB in production)
sessions = {}
users = {
    "demo": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
    "doctor": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # "secret123"
    "admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"   # "admin2024"
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(username: str) -> str:
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "username": username,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return session_id

def get_current_user(request: Request) -> Optional[str]:
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return None
    
    session = sessions[session_id]
    if datetime.now() > session["expires_at"]:
        del sessions[session_id]
        return None
    
    return session["username"]

# Request models
class MedicalQuery(BaseModel):
    question: str
    context: Optional[str] = ""

class SymptomCheck(BaseModel):
    symptoms: List[str]
    age: Optional[int] = None
    gender: Optional[str] = None

# Authentication endpoints
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Assistant - Login</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 400px; 
                margin: 100px auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-container { 
                background: white; 
                padding: 40px; 
                border-radius: 10px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                width: 100%;
                max-width: 400px;
            }
            .logo { text-align: center; margin-bottom: 30px; }
            .logo h1 { color: #333; margin: 0; font-size: 28px; }
            .logo p { color: #666; margin: 5px 0 0 0; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
            input { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #ddd; 
                border-radius: 6px; 
                font-size: 16px;
                box-sizing: border-box;
            }
            input:focus { border-color: #667eea; outline: none; }
            button { 
                width: 100%;
                background: #667eea; 
                color: white; 
                padding: 12px; 
                border: none; 
                border-radius: 6px; 
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
            }
            button:hover { background: #5a6fd8; }
            .demo-info {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 6px;
                margin-top: 20px;
                font-size: 14px;
            }
            .demo-info h4 { margin: 0 0 10px 0; color: #1976d2; }
            .demo-info p { margin: 5px 0; color: #333; }
            .error { color: #d32f2f; margin-top: 10px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">
                <h1>🏥 Medical Assistant</h1>
                <p>Professional Medical Information System</p>
            </div>
            
            <form method="post" action="/login">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            
            <div class="demo-info">
                <h4>Demo Accounts:</h4>
                <p><strong>demo</strong> / password</p>
                <p><strong>doctor</strong> / secret123</p>
                <p><strong>admin</strong> / admin2024</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Handle login form submission."""
    hashed_password = hash_password(password)
    
    if username in users and users[username] == hashed_password:
        session_id = create_session(username)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("session_id", session_id, httponly=True, max_age=86400)
        return response
    else:
        # Return login page with error
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Medical Assistant - Login</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 400px; 
                    margin: 100px auto; 
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .login-container { 
                    background: white; 
                    padding: 40px; 
                    border-radius: 10px; 
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                    width: 100%;
                    max-width: 400px;
                }
                .logo { text-align: center; margin-bottom: 30px; }
                .logo h1 { color: #333; margin: 0; font-size: 28px; }
                .logo p { color: #666; margin: 5px 0 0 0; }
                .form-group { margin: 20px 0; }
                label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
                input { 
                    width: 100%; 
                    padding: 12px; 
                    border: 2px solid #ddd; 
                    border-radius: 6px; 
                    font-size: 16px;
                    box-sizing: border-box;
                }
                input:focus { border-color: #667eea; outline: none; }
                button { 
                    width: 100%;
                    background: #667eea; 
                    color: white; 
                    padding: 12px; 
                    border: none; 
                    border-radius: 6px; 
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                }
                button:hover { background: #5a6fd8; }
                .demo-info {
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-size: 14px;
                }
                .demo-info h4 { margin: 0 0 10px 0; color: #1976d2; }
                .demo-info p { margin: 5px 0; color: #333; }
                .error { color: #d32f2f; margin-top: 10px; text-align: center; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">
                    <h1>🏥 Medical Assistant</h1>
                    <p>Professional Medical Information System</p>
                </div>
                
                <div class="error">❌ Invalid username or password</div>
                
                <form method="post" action="/login">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
                
                <div class="demo-info">
                    <h4>Demo Accounts:</h4>
                    <p><strong>demo</strong> / password</p>
                    <p><strong>doctor</strong> / secret123</p>
                    <p><strong>admin</strong> / admin2024</p>
                </div>
            </div>
        </body>
        </html>
        """, status_code=401)

@app.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_id")
    return response

# Protected routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface (protected)."""
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Query Assistant</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .response { background: #e9ecef; padding: 15px; border-radius: 4px; margin-top: 20px; white-space: pre-wrap; }
            .disclaimer { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin: 10px 0; }
            .loading { display: none; color: #007bff; }
        </style>
    </head>
    <body>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1>🏥 Medical Query Assistant</h1>
            <div style="text-align: right;">
                <span style="color: #666;">Welcome, <strong>{current_user}</strong></span>
                <a href="/logout" style="margin-left: 15px; color: #007bff; text-decoration: none;">Logout</a>
            </div>
        </div>
        
        <div class="disclaimer">
            <strong>⚠️ Disclaimer:</strong> This tool provides general medical information for educational purposes only. 
            Always consult healthcare professionals for medical advice, diagnosis, or treatment.
        </div>

        <div class="container">
            <h2>Medical Question</h2>
            <div class="form-group">
                <label for="question">Ask a medical question:</label>
                <textarea id="question" rows="3" placeholder="e.g., What are the symptoms of diabetes?"></textarea>
            </div>
            <div class="form-group">
                <label for="context">Additional context (optional):</label>
                <input type="text" id="context" placeholder="e.g., Patient is 45 years old">
            </div>
            <button onclick="askQuestion()">Get Medical Information</button>
            <div class="loading" id="loading1">Processing your question...</div>
            <div class="response" id="response1" style="display:none;"></div>
        </div>

        <div class="container">
            <h2>Symptom Checker</h2>
            <div class="form-group">
                <label for="symptoms">Symptoms (comma-separated):</label>
                <input type="text" id="symptoms" placeholder="e.g., headache, fever, fatigue">
            </div>
            <div class="form-group">
                <label for="age">Age (optional):</label>
                <input type="number" id="age" min="0" max="120">
            </div>
            <div class="form-group">
                <label for="gender">Gender (optional):</label>
                <select id="gender">
                    <option value="">Select...</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <button onclick="checkSymptoms()">Analyze Symptoms</button>
            <div class="loading" id="loading2">Analyzing symptoms...</div>
            <div class="response" id="response2" style="display:none;"></div>
        </div>

        <script>
            async function askQuestion() {
                const question = document.getElementById('question').value;
                const context = document.getElementById('context').value;
                
                if (!question.trim()) {
                    alert('Please enter a question');
                    return;
                }
                
                document.getElementById('loading1').style.display = 'block';
                document.getElementById('response1').style.display = 'none';
                
                try {
                    const response = await fetch('/api/medical-query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question, context })
                    });
                    
                    const data = await response.json();
                    document.getElementById('response1').textContent = data.response;
                    document.getElementById('response1').style.display = 'block';
                } catch (error) {
                    document.getElementById('response1').textContent = 'Error: ' + error.message;
                    document.getElementById('response1').style.display = 'block';
                } finally {
                    document.getElementById('loading1').style.display = 'none';
                }
            }
            
            async function checkSymptoms() {
                const symptomsText = document.getElementById('symptoms').value;
                const age = document.getElementById('age').value;
                const gender = document.getElementById('gender').value;
                
                if (!symptomsText.trim()) {
                    alert('Please enter symptoms');
                    return;
                }
                
                const symptoms = symptomsText.split(',').map(s => s.trim()).filter(s => s);
                
                document.getElementById('loading2').style.display = 'block';
                document.getElementById('response2').style.display = 'none';
                
                try {
                    const payload = { symptoms };
                    if (age) payload.age = parseInt(age);
                    if (gender) payload.gender = gender;
                    
                    const response = await fetch('/api/symptom-check', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    document.getElementById('response2').textContent = data.response;
                    document.getElementById('response2').style.display = 'block';
                } catch (error) {
                    document.getElementById('response2').textContent = 'Error: ' + error.message;
                    document.getElementById('response2').style.display = 'block';
                } finally {
                    document.getElementById('loading2').style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/medical-query")
async def medical_query(query: MedicalQuery, request: Request):
    """Handle medical questions (protected)."""
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not medical_client:
        raise HTTPException(status_code=503, detail="Medical service unavailable")
    
    try:
        response = await medical_client.query_medical_question(query.question, query.context)
        return {"response": response, "user": current_user}
    except Exception as e:
        print(f"Medical query error: {e}")
        raise HTTPException(status_code=500, detail=f"Medical service error: {str(e)}")

@app.post("/api/symptom-check")
async def symptom_check(check: SymptomCheck, request: Request):
    """Handle symptom analysis (protected)."""
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not medical_client:
        raise HTTPException(status_code=503, detail="Medical service unavailable")
    
    try:
        response = await medical_client.analyze_symptoms(check.symptoms, check.age, check.gender)
        return {"response": response, "user": current_user}
    except Exception as e:
        print(f"Symptom check error: {e}")
        raise HTTPException(status_code=500, detail=f"Medical service error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if medical_client:
        return {"status": "healthy", "model": medical_client.model_type}
    else:
        return {"status": "degraded", "model": "unavailable"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use PORT environment variable for cloud deployment
    port = int(os.environ.get("PORT", 8000))
    
    # Production-ready configuration
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info",
        access_log=True
    )