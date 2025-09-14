# 🏥 Intelligent Medical Assistant

A comprehensive **Patient-Centric Medical Intelligence System** that combines MCP (Model Context Protocol) server capabilities with an intelligent web interface. This system provides natural language medical queries, patient data analysis, and professional medical insights powered by Gemini AI.

## ✨ Key Features

### 🤖 **Intelligent Medical Assistant**
- **Natural Language Processing** - Ask questions like "What is Ben's sleep summary?"
- **Automatic Tool Routing** - AI decides which patient data to access
- **Conversational Interface** - Single input for all medical queries
- **Professional Medical Responses** - Evidence-based information with disclaimers

### 👥 **Patient Data Management**
- **Real Patient Data** - CSV-based patient records and biometrics
- **Comprehensive Tracking** - Sleep patterns, vital signs, lab results, medications
- **Trend Analysis** - Historical data analysis and insights
- **Multi-Patient Support** - Manage multiple patient records

### 🔧 **Dual Architecture**
- **MCP Server** - Integration with Kiro IDE and other MCP clients
- **Web Application** - Professional web interface with authentication
- **RESTful API** - Programmatic access to medical data and insights

### 📊 **Available Patient Data**
- **Ben Smith** (34M) - Hypertension, Type 2 Diabetes
  - 15 days of detailed sleep data (duration, quality, efficiency)
  - Vital signs tracking (BP, heart rate, glucose, weight)
- **Sarah Jones** (28F) - Asthma
- **Mike Wilson** (45M) - High Cholesterol

## 🚀 Quick Start

### 1. **Installation**

```bash
# Clone and setup
git clone https://github.com/sp2learn/medical-mcp-server.git
cd medical-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configuration**

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
MEDICAL_MODEL=gemini
GOOGLE_API_KEY=your_gemini_api_key_here
DISPLAY_TIMEZONE=America/New_York
```

### 3. **Run the System**

**Web Application:**
```bash
python web_app.py
# Visit: http://localhost:8000
# Login: demo/password, doctor/secret123, admin/admin2024
```

**MCP Server:**
```bash
python server.py
# For integration with Kiro IDE or other MCP clients
```

## 🎯 Usage Examples

### **Natural Language Queries**

The intelligent assistant understands natural language and automatically routes to appropriate tools:

```
🩺 "What is Ben's sleep summary for the past week?"
→ Analyzes sleep data, provides trends and insights

📊 "Show me Ben's blood pressure trends"
→ Reviews vital signs, identifies patterns

💊 "What medications is Ben taking?"
→ Lists current medications and adherence data

🔍 "What are the symptoms of diabetes?"
→ Provides general medical information

📈 "Compare Ben's glucose levels over time"
→ Analyzes lab data and trends
```

### **MCP Integration**

Add to your Kiro IDE configuration (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "medical-query": {
      "command": "/path/to/medical-mcp-server/venv/bin/python",
      "args": ["/path/to/medical-mcp-server/server.py"],
      "disabled": false,
      "autoApprove": [
        "medical_query",
        "symptom_checker", 
        "get_patient_sleep_pattern",
        "get_patient_vitals",
        "get_patient_labs",
        "get_medication_adherence",
        "get_patient_activity",
        "get_patient_overview"
      ]
    }
  }
}
```

## 🛠️ Available Tools

### **MCP Tools (8 total)**

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `medical_query` | General medical Q&A | "What causes hypertension?" |
| `symptom_checker` | Symptom analysis | Analyze: headache, fever, fatigue |
| `get_patient_sleep_pattern` | Sleep data analysis | Ben's sleep for 30 days |
| `get_patient_vitals` | Vital signs summary | Ben's latest BP readings |
| `get_patient_labs` | Laboratory results | Ben's glucose trends |
| `get_medication_adherence` | Medication compliance | Ben's medication adherence |
| `get_patient_activity` | Physical activity data | Ben's activity levels |
| `get_patient_overview` | Complete patient summary | Ben's full medical profile |

### **Tool Management**

```bash
# List all tools and their status
python manage_tools.py list

# Show detailed tool information  
python manage_tools.py details get_patient_sleep_pattern

# Enable/disable tools
python manage_tools.py enable medical_query
python manage_tools.py disable symptom_checker
```

## 📁 Project Structure

```
medical-mcp-server/
├── 🤖 Core Intelligence
│   ├── intelligent_medical_assistant.py  # Natural language processing
│   ├── medical_client.py                 # AI model integration
│   └── patient_data_manager.py           # Patient data management
├── 🌐 Web Interface  
│   ├── web_app.py                        # FastAPI web application
│   ├── templates/                        # HTML templates
│   │   ├── dashboard.html                # Main interface
│   │   ├── login.html                    # Authentication
│   │   └── base.html                     # Base template
│   └── static/                           # CSS, JavaScript, assets
├── 🔧 MCP Server
│   ├── server.py                         # MCP protocol server
│   ├── tool_config.py                    # Centralized tool configuration
│   └── manage_tools.py                   # Tool management CLI
├── 📊 Patient Data
│   └── data/
│       ├── patients.csv                  # Patient demographics
│       ├── ben_sleep_data.csv            # Ben's sleep metrics
│       └── ben_vitals_data.csv           # Ben's vital signs
└── 🚀 Deployment
    ├── Dockerfile                        # Container configuration
    ├── docker-compose.yml                # Multi-service setup
    └── render.yaml                       # Render deployment config
```

## 🌐 Deployment

### **Local Development**
```bash
source venv/bin/activate
python web_app.py
# Access: http://localhost:8000
```

### **Cloud Deployment (Render)**
1. Push to GitHub
2. Connect repository to Render
3. Set environment variables:
   - `MEDICAL_MODEL=gemini`
   - `GOOGLE_API_KEY=your_key`
4. Deploy automatically

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t medical-mcp-server .
docker run -p 8000:8000 --env-file .env medical-mcp-server
```

## 🔐 Authentication & Security

### **Web Interface**
- **Session-based authentication** with secure cookies
- **Role-based access** (demo, doctor, admin accounts)
- **24-hour session expiration**
- **HTTPS ready** for production deployment

### **Demo Accounts**
| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `demo` | `password` | Patient | Basic demo access |
| `doctor` | `secret123` | Healthcare Provider | Full medical access |
| `admin` | `admin2024` | Administrator | System administration |

## 📈 Patient Data Format

### **Patient Demographics (`patients.csv`)**
```csv
patient_id,first_name,last_name,age,gender,conditions,medications,last_visit
ben_smith,Ben,Smith,34,male,"hypertension,type_2_diabetes","metformin,lisinopril",2024-01-15
```

### **Sleep Data (`ben_sleep_data.csv`)**
```csv
date,sleep_hours,bedtime,wake_time,sleep_quality,deep_sleep_minutes,rem_sleep_minutes
2024-09-14,7.2,22:30,05:42,good,85,92
```

### **Vital Signs (`ben_vitals_data.csv`)**
```csv
date,systolic_bp,diastolic_bp,heart_rate,temperature_f,weight_kg,glucose_mg_dl
2024-09-14,142,88,72,98.6,78.2,156
```

## 🧪 Testing

```bash
# Test MCP server functionality
python test_server.py

# Test tool configuration
python manage_tools.py list

# Test web application
curl http://localhost:8000/health

# Run comprehensive tests
./run_tests.sh
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/sp2learn/medical-mcp-server/issues)
- **Documentation**: See individual module docstrings
- **Examples**: Check the `examples/` directory

## ⚠️ Medical Disclaimer

This tool provides general medical information for educational and professional reference purposes only. It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions regarding medical conditions or treatment decisions.

---

**Built with ❤️ for healthcare professionals and medical AI research**