#!/usr/bin/env python3
"""
Medical Query Web App - Clean version with templates
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import secrets
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

from medical_client import MedicalClient
from patient_data_manager import PatientDataManager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Medical Query API", description="Medical information web service")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize medical client and patient manager with error handling
try:
    medical_client = MedicalClient()
    patient_manager = PatientDataManager()
    print(f"✅ Medical client initialized with model: {medical_client.model_type}")
    print(f"✅ Patient data manager initialized with {len(patient_manager.patients)} patients")
except Exception as e:
    print(f"❌ Failed to initialize services: {e}")
    medical_client = None
    patient_manager = None

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

def get_formatted_timestamp() -> str:
    """Get current timestamp in a user-friendly format."""
    try:
        # Get timezone from environment variable or default to Eastern Time
        timezone_name = os.getenv("DISPLAY_TIMEZONE", "America/New_York")
        local_tz = pytz.timezone(timezone_name)
        current_time = datetime.now(local_tz).strftime("%B %d, %Y at %I:%M %p %Z")
        return current_time
    except Exception as e:
        # Fallback to UTC if timezone handling fails
        print(f"Timezone error: {e}, falling back to UTC")
        return datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")

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

class PatientQuery(BaseModel):
    patient_identifier: str
    query_type: str  # sleep, vitals, labs, medications, activity, overview
    days: Optional[int] = 30

# Authentication endpoints
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login form submission."""
    hashed_password = hash_password(password)
    
    if username in users and users[username] == hashed_password:
        session_id = create_session(username)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("session_id", session_id, httponly=True, max_age=86400)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        }, status_code=401)

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
    
    # Get current time in a user-friendly format
    current_time = get_formatted_timestamp()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user,
        "current_time": current_time
    })

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

@app.post("/api/patient-query")
async def patient_query(query: PatientQuery, request: Request):
    """Handle patient data queries (protected)."""
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not patient_manager:
        raise HTTPException(status_code=503, detail="Patient data service unavailable")
    
    try:
        # Find patient
        patient = patient_manager.find_patient(query.patient_identifier)
        if not patient:
            available_patients = ", ".join([p["name"] for p in patient_manager.patients.values()])
            return {"response": f"Patient '{query.patient_identifier}' not found. Available patients: {available_patients}"}
        
        # Route to appropriate data retrieval method
        if query.query_type == "sleep":
            data = patient_manager.get_sleep_pattern(patient["id"], query.days)
            response = f"Sleep Pattern Analysis for {data['patient_name']}\n"
            response += f"Period: {data['period']}\n"
            response += f"Average Sleep: {data['average_sleep_hours']} hours per night\n\n"
            response += f"Sleep Quality Distribution:\n"
            for quality, count in data['sleep_quality_distribution'].items():
                response += f"  {quality.title()}: {count} nights\n"
            response += f"\nSummary: {data['summary']}"
            
        elif query.query_type == "vitals":
            data = patient_manager.get_vitals_summary(patient["id"])
            response = f"Vital Signs Summary for {data['patient_name']}\n\n"
            if data['latest_reading']:
                latest = data['latest_reading']
                response += f"Latest Reading ({latest['date']}):\n"
                response += f"  Blood Pressure: {latest['blood_pressure']['systolic']}/{latest['blood_pressure']['diastolic']} mmHg\n"
                response += f"  Heart Rate: {latest['heart_rate']} bpm\n"
                response += f"  Temperature: {latest['temperature']}°F\n"
                response += f"  Weight: {latest['weight']} lbs\n\n"
            response += f"Average BP: {data['average_bp']} mmHg\n"
            response += f"Known Conditions: {', '.join(data['conditions'])}"
            
        elif query.query_type == "labs":
            data = patient_manager.get_lab_results(patient["id"])
            response = f"Laboratory Results for {data['patient_name']}\n\n"
            if data['latest_labs']:
                latest = data['latest_labs']
                response += f"Latest Labs ({latest['date']}):\n"
                response += f"  Glucose: {latest['glucose']} mg/dL\n"
                response += f"  HbA1c: {latest['hba1c']}%\n"
                response += f"  Total Cholesterol: {latest['cholesterol']['total']} mg/dL\n"
                response += f"  LDL: {latest['cholesterol']['ldl']} mg/dL\n"
                response += f"  HDL: {latest['cholesterol']['hdl']} mg/dL\n"
                response += f"  Creatinine: {latest['kidney_function']['creatinine']} mg/dL\n"
                
        elif query.query_type == "medications":
            data = patient_manager.get_medication_adherence(patient["id"])
            response = f"Medication Adherence for {data['patient_name']}\n\n"
            response += f"Overall Adherence Rate: {data['overall_adherence']}%\n\n"
            for med in data['medications']:
                response += f"{med['medication'].title()}:\n"
                response += f"  Adherence Rate: {med['adherence_rate']}%\n"
                response += f"  Prescribed: {med['prescribed_dose']}\n\n"
                
        elif query.query_type == "activity":
            data = patient_manager.get_activity_summary(patient["id"], query.days)
            response = f"Physical Activity Summary for {data['patient_name']}\n"
            response += f"Period: {data['period']}\n\n"
            response += f"Average Daily Steps: {data['average_daily_steps']:,}\n"
            response += f"Average Active Minutes: {data['average_active_minutes']} minutes/day\n"
            
        elif query.query_type == "overview":
            data = patient_manager.get_patient_overview(patient["id"])
            info = data['patient_info']
            response = f"Patient Overview: {info['name']}\n\n"
            response += f"Demographics:\n"
            response += f"  Age: {info['age']} years\n"
            response += f"  Gender: {info['gender'].title()}\n"
            response += f"  Last Visit: {info['last_visit']}\n\n"
            response += f"Conditions: {', '.join(info['conditions'])}\n"
            response += f"Medications: {', '.join(info['medications'])}\n\n"
            response += f"Recent Summary:\n"
            response += f"  Sleep: {data['sleep_summary']}\n"
            response += f"  Activity: {data['activity_summary']}\n"
        else:
            response = f"Unknown query type: {query.query_type}"
        
        return {"response": response, "user": current_user}
        
    except Exception as e:
        print(f"Patient query error: {e}")
        raise HTTPException(status_code=500, detail=f"Patient data service error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if medical_client and patient_manager:
        return {
            "status": "healthy", 
            "model": medical_client.model_type,
            "patients": len(patient_manager.patients)
        }
    else:
        return {"status": "degraded", "services": "unavailable"}

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