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
        const additionalContext = document.getElementById('additional_context').value;
        const priority = document.getElementById('query_priority').value;
        const followUpRequired = document.getElementById('follow_up_required').checked;
        const detailedAnalysis = document.getElementById('detailed_analysis').checked;
        const files = document.getElementById('medical_files').files;
        
        if (!query.trim()) {
            this.showAlert('Please enter your medical question');
            return;
        }
        
        this.showLoading('loading_main', true);
        this.hideResponse('response_main');
        
        try {
            // Build enhanced query with context
            let enhancedQuery = query;
            
            if (additionalContext.trim()) {
                enhancedQuery += `\n\nAdditional Clinical Context: ${additionalContext}`;
            }
            
            if (detailedAnalysis) {
                enhancedQuery += '\n\nPlease provide detailed analysis with clinical insights.';
            }
            
            if (followUpRequired) {
                enhancedQuery += '\n\nFollow-up recommendations requested.';
            }
            
            if (priority !== 'routine') {
                enhancedQuery += `\n\nPriority: ${priority.toUpperCase()}`;
            }
            
            // Handle file uploads (for now, just mention them)
            if (files.length > 0) {
                const fileNames = Array.from(files).map(f => f.name).join(', ');
                enhancedQuery += `\n\nAttached Files: ${fileNames} (Note: File analysis not yet implemented)`;
            }
            
            const response = await this.makeRequest('/api/intelligent-query', {
                query: enhancedQuery,
                context: {
                    priority: priority,
                    followUp: followUpRequired,
                    detailed: detailedAnalysis,
                    fileCount: files.length
                }
            });
            
            this.showResponse('response_main', response.response);
            
            // Show priority indicator if urgent/stat
            if (priority !== 'routine') {
                this.showPriorityIndicator(priority);
            }
            
        } catch (error) {
            this.showResponse('response_main', 'Error: ' + error.message);
        } finally {
            this.showLoading('loading_main', false);
        }
    }
    
    // Show priority indicator
    showPriorityIndicator(priority) {
        const responseElement = document.getElementById('response_main');
        if (responseElement && priority !== 'routine') {
            const priorityBadge = document.createElement('div');
            priorityBadge.style.cssText = `
                background: ${priority === 'stat' ? '#dc3545' : '#fd7e14'};
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
                margin-bottom: 10px;
                display: inline-block;
            `;
            priorityBadge.textContent = `${priority.toUpperCase()} PRIORITY`;
            responseElement.insertBefore(priorityBadge, responseElement.firstChild);
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