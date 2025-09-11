// Authentication Module
class AuthManager {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
    }

    async login(username, password) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                this.token = data.data.token;
                this.user = data.data.user;
                
                localStorage.setItem('token', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));
                
                return { success: true, user: this.user };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Network error occurred' };
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // Redirect to login page
        showLoginPage();
    }

    isAuthenticated() {
        return this.token !== null && this.user !== null;
    }

    getToken() {
        return this.token;
    }

    getUser() {
        return this.user;
    }

    hasRole(role) {
        return this.user && this.user.role === role;
    }

    hasAnyRole(roles) {
        return this.user && roles.includes(this.user.role);
    }

    isAdmin() {
        return this.hasRole('admin');
    }

    isManager() {
        return this.hasRole('manager');
    }

    isDriver() {
        return this.hasRole('driver');
    }

    canManage() {
        return this.hasAnyRole(['admin', 'manager']);
    }

    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async checkTokenValidity() {
        if (!this.token) return false;

        try {
            const response = await fetch('/api/auth/me', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.user = data.data;
                    localStorage.setItem('user', JSON.stringify(this.user));
                    return true;
                }
            }
            
            // Token is invalid, logout
            this.logout();
            return false;
        } catch (error) {
            console.error('Token validation error:', error);
            this.logout();
            return false;
        }
    }
}

// Global auth instance
const auth = new AuthManager();

// Login form handler
function initializeAuth() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showToast('Please enter both username and password', 'error');
                return;
            }

            showLoading(true);
            
            const result = await auth.login(username, password);
            
            showLoading(false);
            
            if (result.success) {
                showToast('Login successful!', 'success');
                initializeApp();
            } else {
                showToast(result.message || 'Login failed', 'error');
            }
        });
    }
}

// Check authentication status on page load
function checkAuthStatus() {
    if (auth.isAuthenticated()) {
        // Validate token
        auth.checkTokenValidity().then(isValid => {
            if (isValid) {
                initializeApp();
            } else {
                showLoginPage();
            }
        });
    } else {
        showLoginPage();
    }
}

// Show login page
function showLoginPage() {
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('mainNavbar').style.display = 'none';
    document.getElementById('mainContent').style.display = 'none';
}

// Show main application
function showMainApp() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('mainNavbar').style.display = 'block';
    document.getElementById('mainContent').style.display = 'block';
    
    // Update navigation based on user role
    updateNavigationForRole();
    
    // Update current username
    document.getElementById('currentUsername').textContent = auth.getUser().username;
}

// Update navigation based on user role
function updateNavigationForRole() {
    const user = auth.getUser();
    
    // Show/hide navigation items based on role
    if (user.role === 'admin') {
        document.getElementById('usersNav').style.display = 'block';
    } else {
        document.getElementById('usersNav').style.display = 'none';
    }
    
    // Drivers can only see trips assigned to them
    if (user.role === 'driver') {
        // Additional restrictions can be implemented here
    }
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        auth.logout();
        showToast('Logged out successfully', 'info');
    }
}

// Profile function (placeholder)
function showProfile() {
    showToast('Profile page coming soon!', 'info');
}

