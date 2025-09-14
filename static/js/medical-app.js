/**
 * Medical MCP Server - Frontend JavaScript
 */

class MedicalApp {
    constructor() {
        this.init();
    }

    init() {
        console.log('Medical App initialized');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add any global event listeners here
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM loaded');
        });
    }

    // Medical Query Functions
    async askQuestion() {
        const question = document.getElementById('question').value;
        const context = document.getElementById('context').value;
        
        if (!question.trim()) {
            this.showAlert('Please enter a question');
            return;
        }
        
        this.showLoading('loading1', true);
        this.hideResponse('response1');
        
        try {
            const response = await this.makeRequest('/api/medical-query', {
                question,
                context
            });
            
            this.showResponse('response1', response.response);
        } catch (error) {
            this.showResponse('response1', 'Error: ' + error.message);
        } finally {
            this.showLoading('loading1', false);
        }
    }

    // Symptom Checker Functions
    async checkSymptoms() {
        const symptomsText = document.getElementById('symptoms').value;
        const age = document.getElementById('age').value;
        const gender = document.getElementById('gender').value;
        
        if (!symptomsText.trim()) {
            this.showAlert('Please enter symptoms');
            return;
        }
        
        const symptoms = symptomsText.split(',').map(s => s.trim()).filter(s => s);
        
        this.showLoading('loading2', true);
        this.hideResponse('response2');
        
        try {
            const payload = { symptoms };
            if (age) payload.age = parseInt(age);
            if (gender) payload.gender = gender;
            
            const response = await this.makeRequest('/api/symptom-check', payload);
            this.showResponse('response2', response.response);
        } catch (error) {
            this.showResponse('response2', 'Error: ' + error.message);
        } finally {
            this.showLoading('loading2', false);
        }
    }

    // Patient Query Functions
    async queryPatientData() {
        const patientName = document.getElementById('patient_name').value;
        const queryType = document.getElementById('query_type').value;
        const days = document.getElementById('days').value;
        
        if (!patientName.trim()) {
            this.showAlert('Please enter a patient name or ID');
            return;
        }
        
        this.showLoading('loading3', true);
        this.hideResponse('response3');
        
        try {
            const payload = { 
                patient_identifier: patientName,
                query_type: queryType,
                days: parseInt(days) || 30
            };
            
            const response = await this.makeRequest('/api/patient-query', payload);
            this.showResponse('response3', response.response);
        } catch (error) {
            this.showResponse('response3', 'Error: ' + error.message);
        } finally {
            this.showLoading('loading3', false);
        }
    }

    // Utility Functions
    async makeRequest(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }

    showLoading(elementId, show) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = show ? 'block' : 'none';
        }
    }

    showResponse(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
            element.style.display = 'block';
        }
    }

    hideResponse(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    }

    showAlert(message) {
        alert(message);
    }

    // Form Helpers
    clearForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
    }

    // Patient Helper Functions
    fillPatientExample(patientName) {
        const patientField = document.getElementById('patient_name');
        if (patientField) {
            patientField.value = patientName;
        }
    }

    // Quick Actions
    setupQuickActions() {
        // Add quick action buttons for common queries
        const quickActions = [
            { text: 'Ben Sleep Pattern', action: () => this.quickPatientQuery('Ben Smith', 'sleep') },
            { text: 'Sarah Vitals', action: () => this.quickPatientQuery('Sarah Jones', 'vitals') },
            { text: 'Mike Labs', action: () => this.quickPatientQuery('Mike Wilson', 'labs') }
        ];

        // You can add these to the UI if needed
        return quickActions;
    }

    quickPatientQuery(patient, type) {
        document.getElementById('patient_name').value = patient;
        document.getElementById('query_type').value = type;
        this.queryPatientData();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.medicalApp = new MedicalApp();
});

// Global functions for HTML onclick handlers
function askQuestion() {
    window.medicalApp.askQuestion();
}

function checkSymptoms() {
    window.medicalApp.checkSymptoms();
}

function queryPatientData() {
    window.medicalApp.queryPatientData();
}