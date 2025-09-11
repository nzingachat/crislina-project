// API Utility Module
class ApiClient {
    constructor() {
        this.baseUrl = '/api';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        // Add authentication headers if user is logged in
        if (auth.isAuthenticated()) {
            defaultOptions.headers.Authorization = `Bearer ${auth.getToken()}`;
        }

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();

            // Handle authentication errors
            if (response.status === 401) {
                auth.logout();
                showToast('Session expired. Please login again.', 'error');
                return null;
            }

            return {
                success: response.ok,
                status: response.status,
                data: data
            };
        } catch (error) {
            console.error('API request error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Vehicles API
    async getVehicles(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.get(`/vehicles?${params}`);
    }

    async getVehicle(id) {
        return this.get(`/vehicles/${id}`);
    }

    async createVehicle(vehicleData) {
        return this.post('/vehicles', vehicleData);
    }

    async updateVehicle(id, vehicleData) {
        return this.put(`/vehicles/${id}`, vehicleData);
    }

    async deleteVehicle(id) {
        return this.delete(`/vehicles/${id}`);
    }

    async getVehicleStats(id) {
        return this.get(`/vehicles/${id}/stats`);
    }

    // Drivers API
    async getDrivers(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.get(`/drivers?${params}`);
    }

    async getDriver(id) {
        return this.get(`/drivers/${id}`);
    }

    async createDriver(driverData) {
        return this.post('/drivers', driverData);
    }

    async updateDriver(id, driverData) {
        return this.put(`/drivers/${id}`, driverData);
    }

    async deleteDriver(id) {
        return this.delete(`/drivers/${id}`);
    }

    async getDriverStats(id) {
        return this.get(`/drivers/${id}/stats`);
    }

    // Trips API
    async getTrips(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.get(`/trips?${params}`);
    }

    async getTrip(id) {
        return this.get(`/trips/${id}`);
    }

    async createTrip(tripData) {
        return this.post('/trips', tripData);
    }

    async updateTrip(id, tripData) {
        return this.put(`/trips/${id}`, tripData);
    }

    async deleteTrip(id) {
        return this.delete(`/trips/${id}`);
    }

    async startTrip(id) {
        return this.post(`/trips/${id}/start`);
    }

    async completeTrip(id, data = {}) {
        return this.post(`/trips/${id}/complete`, data);
    }

    // Maintenance API
    async getMaintenance(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.get(`/maintenance?${params}`);
    }

    async getMaintenanceRecord(id) {
        return this.get(`/maintenance/${id}`);
    }

    async createMaintenanceRecord(maintenanceData) {
        return this.post('/maintenance', maintenanceData);
    }

    async updateMaintenanceRecord(id, maintenanceData) {
        return this.put(`/maintenance/${id}`, maintenanceData);
    }

    async deleteMaintenanceRecord(id) {
        return this.delete(`/maintenance/${id}`);
    }

    async getMaintenanceStats(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.get(`/maintenance/stats?${params}`);
    }

    // Analytics API
    async getDashboardStats() {
        return this.get('/analytics/dashboard');
    }

    async getFuelConsumptionTrends(days = 30) {
        return this.get(`/analytics/fuel-consumption?days=${days}`);
    }

    async getTripsPerVehicle() {
        return this.get('/analytics/trips-per-vehicle');
    }

    async getTripsPerDriver() {
        return this.get('/analytics/trips-per-driver');
    }

    async getMaintenanceCostTrends(months = 12) {
        return this.get(`/analytics/maintenance-costs?months=${months}`);
    }

    async getVehicleUtilization(days = 30) {
        return this.get(`/analytics/vehicle-utilization?days=${days}`);
    }

    async getFuelEfficiency() {
        return this.get('/analytics/fuel-efficiency');
    }

    // Users API (Admin only)
    async getUsers() {
        return this.get('/users');
    }

    async getUser(id) {
        return this.get(`/users/${id}`);
    }

    async updateUser(id, userData) {
        return this.put(`/users/${id}`, userData);
    }

    async deleteUser(id) {
        return this.delete(`/users/${id}`);
    }

    async changePassword(currentPassword, newPassword) {
        return this.post('/auth/change-password', {
            current_password: currentPassword,
            new_password: newPassword
        });
    }
}

// Global API client instance
const api = new ApiClient();

// Utility functions
function showLoading(show = true) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toastId = 'toast-' + Date.now();
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };

    const colorMap = {
        success: 'text-success',
        error: 'text-danger',
        warning: 'text-warning',
        info: 'text-primary'
    };

    const toastHtml = `
        <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="${iconMap[type]} ${colorMap[type]} me-2"></i>
                <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: type === 'error' ? 5000 : 3000
    });
    
    toast.show();

    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Format date utility
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Format datetime utility
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format currency utility
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format number utility
function formatNumber(number, decimals = 2) {
    if (number === null || number === undefined) return '0';
    return Number(number).toFixed(decimals);
}

// Get status badge HTML
function getStatusBadge(status) {
    const statusMap = {
        active: 'bg-success',
        inactive: 'bg-secondary',
        maintenance: 'bg-warning',
        planned: 'bg-primary',
        in_progress: 'bg-info',
        completed: 'bg-success',
        cancelled: 'bg-danger',
        scheduled: 'bg-primary',
        routine: 'bg-info',
        repair: 'bg-warning',
        emergency: 'bg-danger'
    };

    const badgeClass = statusMap[status] || 'bg-secondary';
    return `<span class="badge ${badgeClass}">${status.replace('_', ' ').toUpperCase()}</span>`;
}

