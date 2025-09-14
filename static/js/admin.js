/**
 * Admin Dashboard JavaScript
 * Handles tool provider management, API configuration, and system administration
 */

class AdminDashboard {
    constructor() {
        this.currentSection = 'providers';
        this.providers = [];
        this.init();
    }

    init() {
        console.log('Admin Dashboard initialized');
        this.loadProviders();
        this.loadStatistics();
    }

    // Section Management
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.admin-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Remove active class from all nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected section
        document.getElementById(`${sectionName}-section`).style.display = 'block';
        
        // Add active class to clicked button
        event.target.classList.add('active');
        
        this.currentSection = sectionName;
        
        // Load section-specific data
        switch(sectionName) {
            case 'providers':
                this.loadProviders();
                break;
            case 'statistics':
                this.loadStatistics();
                break;
            case 'api-keys':
                this.loadApiKeys();
                break;
            case 'logs':
                this.loadLogs();
                break;
        }
    }

    // Provider Management
    async loadProviders() {
        try {
            this.showLoading('providers-loading', true);
            const response = await this.makeRequest('/api/admin/providers', {}, 'GET');
            this.providers = response.providers || [];
            this.renderProviders();
        } catch (error) {
            console.error('Error loading providers:', error);
            this.showError('Failed to load providers');
        } finally {
            this.showLoading('providers-loading', false);
        }
    }

    renderProviders() {
        const container = document.getElementById('providers-list');
        if (!this.providers.length) {
            container.innerHTML = '<div class="no-data">No tool providers configured. Add your first provider to get started.</div>';
            return;
        }

        container.innerHTML = this.providers.map(provider => `
            <div class="provider-card">
                <div class="provider-header">
                    <h3>${provider.name}</h3>
                    <div class="provider-status ${provider.enabled ? 'enabled' : 'disabled'}">
                        ${provider.enabled ? '🟢 Active' : '🔴 Disabled'}
                    </div>
                </div>
                
                <div class="provider-info">
                    <p><strong>Company:</strong> ${provider.provider_company}</p>
                    <p><strong>Categories:</strong> ${provider.medical_categories.join(', ')}</p>
                    <p><strong>Endpoint:</strong> ${provider.server_url}${provider.endpoint_path}</p>
                    <p><strong>Invocations:</strong> ${provider.total_invocations}</p>
                    <p><strong>Success Rate:</strong> ${provider.success_rate.toFixed(1)}%</p>
                </div>
                
                <div class="provider-actions">
                    <button onclick="adminDashboard.testProvider('${provider.id}')" class="btn-test">🧪 Test</button>
                    <button onclick="adminDashboard.editProvider('${provider.id}')" class="btn-edit">✏️ Edit</button>
                    <button onclick="adminDashboard.toggleProvider('${provider.id}')" class="btn-toggle">
                        ${provider.enabled ? '⏸️ Disable' : '▶️ Enable'}
                    </button>
                    <button onclick="adminDashboard.deleteProvider('${provider.id}')" class="btn-delete">🗑️ Delete</button>
                </div>
            </div>
        `).join('');
    }

    async testProvider(providerId) {
        try {
            const response = await this.makeRequest(`/api/admin/providers/${providerId}/test`, {}, 'POST');
            if (response.success) {
                this.showSuccess(`Provider test successful! Response time: ${response.response_time.toFixed(2)}s`);
            } else {
                this.showError(`Provider test failed: ${response.error}`);
            }
            this.loadProviders(); // Refresh to show updated stats
        } catch (error) {
            this.showError('Failed to test provider');
        }
    }

    async toggleProvider(providerId) {
        try {
            const provider = this.providers.find(p => p.id === providerId);
            const newStatus = !provider.enabled;
            
            await this.makeRequest(`/api/admin/providers/${providerId}`, {
                enabled: newStatus
            }, 'PUT');
            
            this.showSuccess(`Provider ${newStatus ? 'enabled' : 'disabled'} successfully`);
            this.loadProviders();
        } catch (error) {
            this.showError('Failed to update provider status');
        }
    }

    async deleteProvider(providerId) {
        if (!confirm('Are you sure you want to delete this provider? This action cannot be undone.')) {
            return;
        }

        try {
            await this.makeRequest(`/api/admin/providers/${providerId}`, {}, 'DELETE');
            this.showSuccess('Provider deleted successfully');
            this.loadProviders();
        } catch (error) {
            this.showError('Failed to delete provider');
        }
    }

    // Add Provider Form
    async submitProviderForm(event) {
        event.preventDefault();
        
        try {
            const formData = this.getFormData();
            const response = await this.makeRequest('/api/admin/providers', formData, 'POST');
            
            if (response.success) {
                this.showSuccess('Provider added successfully!');
                document.getElementById('add-provider-form').reset();
                this.showSection('providers');
            } else {
                this.showError(response.error || 'Failed to add provider');
            }
        } catch (error) {
            this.showError('Failed to add provider');
        }
    }

    getFormData() {
        const categories = Array.from(document.querySelectorAll('.checkbox-grid input:checked'))
            .map(cb => cb.value);

        return {
            id: document.getElementById('provider_id').value,
            name: document.getElementById('provider_name').value,
            description: document.getElementById('provider_description').value,
            provider_company: document.getElementById('provider_company').value,
            contact_email: document.getElementById('contact_email').value,
            server_url: document.getElementById('server_url').value,
            endpoint_path: document.getElementById('endpoint_path').value,
            http_method: document.getElementById('http_method').value,
            content_type: document.getElementById('content_type').value,
            auth_type: document.getElementById('auth_type').value,
            api_key: document.getElementById('api_key').value,
            medical_categories: categories,
            rate_limit: parseInt(document.getElementById('rate_limit').value),
            timeout_seconds: parseInt(document.getElementById('timeout_seconds').value)
        };
    }

    // Statistics
    async loadStatistics() {
        try {
            const response = await this.makeRequest('/api/admin/statistics', {}, 'GET');
            this.renderStatistics(response.stats);
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    renderStatistics(stats) {
        const container = document.getElementById('stats-content');
        container.innerHTML = `
            <div class="stat-card">
                <h3>📊 Overview</h3>
                <div class="stat-item">
                    <span class="stat-label">Total Providers:</span>
                    <span class="stat-value">${stats.total_providers}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Active Providers:</span>
                    <span class="stat-value">${stats.enabled_providers}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Invocations:</span>
                    <span class="stat-value">${stats.total_invocations.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average Success Rate:</span>
                    <span class="stat-value">${stats.avg_success_rate.toFixed(1)}%</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>🏥 Medical Categories</h3>
                ${Object.entries(stats.medical_categories).map(([category, count]) => `
                    <div class="stat-item">
                        <span class="stat-label">${category.charAt(0).toUpperCase() + category.slice(1)}:</span>
                        <span class="stat-value">${count}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // API Keys Management
    async loadApiKeys() {
        // Implementation for API key management
        const container = document.getElementById('api-keys-list');
        container.innerHTML = '<div class="no-data">API key management coming soon...</div>';
    }

    async generateNewApiKey() {
        try {
            const response = await this.makeRequest('/api/admin/generate-api-key', {}, 'POST');
            this.showSuccess(`New API key generated: ${response.api_key}`);
        } catch (error) {
            this.showError('Failed to generate API key');
        }
    }

    // Logs Management
    async loadLogs() {
        const container = document.getElementById('logs-content');
        container.innerHTML = '<div class="no-data">System logs coming soon...</div>';
    }

    // Utility Functions
    async makeRequest(url, data, method = 'POST') {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };

        if (method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
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

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 6px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }

    generateApiKey() {
        const apiKey = 'med_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        document.getElementById('api_key').value = apiKey;
    }
}

// Authentication field toggling
function toggleAuthFields() {
    const authType = document.getElementById('auth_type').value;
    const authFields = document.getElementById('auth-fields');
    
    let fieldsHtml = '';
    
    switch(authType) {
        case 'api_key':
            fieldsHtml = `
                <div class="form-group">
                    <label for="api_key">API Key:</label>
                    <input type="password" id="api_key" placeholder="Enter API key">
                    <button type="button" onclick="adminDashboard.generateApiKey()">Generate</button>
                </div>
            `;
            break;
        case 'bearer_token':
            fieldsHtml = `
                <div class="form-group">
                    <label for="bearer_token">Bearer Token:</label>
                    <input type="password" id="bearer_token" placeholder="Enter bearer token">
                </div>
            `;
            break;
        case 'basic_auth':
            fieldsHtml = `
                <div class="form-row">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" placeholder="Enter password">
                    </div>
                </div>
            `;
            break;
        case 'oauth2':
            fieldsHtml = `
                <div class="form-group">
                    <label for="client_id">Client ID:</label>
                    <input type="text" id="client_id" placeholder="Enter OAuth client ID">
                </div>
                <div class="form-group">
                    <label for="client_secret">Client Secret:</label>
                    <input type="password" id="client_secret" placeholder="Enter OAuth client secret">
                </div>
            `;
            break;
    }
    
    authFields.innerHTML = fieldsHtml;
}

// Global functions
function showSection(sectionName) {
    adminDashboard.showSection(sectionName);
}

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
    
    // Add form submit handler
    document.getElementById('add-provider-form').addEventListener('submit', (e) => {
        adminDashboard.submitProviderForm(e);
    });
});