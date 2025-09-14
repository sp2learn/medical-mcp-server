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
        this.updatePageLoadTime();
    }

    setupEventListeners() {
        // Add any global event listeners here
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM loaded');
        });
    }

    // Intelligent Medical Query Function
    async processIntelligentQuery() {
        const query = document.getElementById('medical_query').value;
        
        if (!query.trim()) {
            this.showAlert('Please enter your medical question');
            return;
        }
        
        this.showLoading('loading_main', true);
        this.hideResponse('response_main');
        
        try {
            const response = await this.makeRequest('/api/intelligent-query', {
                query: query
            });
            
            this.showResponse('response_main', response.response);
        } catch (error) {
            this.showResponse('response_main', 'Error: ' + error.message);
        } finally {
            this.showLoading('loading_main', false);
        }
    }

    // Example Functions
    fillExample(exampleText) {
        document.getElementById('medical_query').value = exampleText;
        // Auto-focus on the query button
        document.querySelector('button[onclick="processIntelligentQuery()"]').focus();
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

    // Timestamp utilities
    updatePageLoadTime() {
        const now = new Date();
        const timeString = now.toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            timeZoneName: 'short'
        });
        
        // Update any elements with class 'page-load-time'
        const elements = document.querySelectorAll('.page-load-time');
        elements.forEach(el => {
            el.textContent = timeString;
        });
        
        console.log('Page loaded at:', timeString);
    }

    refreshTimestamp() {
        // Refresh the current page to get updated server timestamp
        window.location.reload();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.medicalApp = new MedicalApp();
});

// Global functions for HTML onclick handlers
function processIntelligentQuery() {
    window.medicalApp.processIntelligentQuery();
}

function fillExample(exampleText) {
    window.medicalApp.fillExample(exampleText);
}