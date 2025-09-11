// Main Application Module
let currentPage = 'dashboard';

// Initialize the application
function initializeApp() {
    if (auth.isAuthenticated()) {
        showMainApp();
        showDashboard();
    } else {
        showLoginPage();
    }
}

// Navigation functions
function showDashboard() {
    currentPage = 'dashboard';
    updateActiveNavigation('dashboard');
    loadDashboard();
}

function showVehicles() {
    currentPage = 'vehicles';
    updateActiveNavigation('vehicles');
    loadVehicles();
}

function showDrivers() {
    currentPage = 'drivers';
    updateActiveNavigation('drivers');
    loadDrivers();
}

function showTrips() {
    currentPage = 'trips';
    updateActiveNavigation('trips');
    loadTrips();
}

function showMaintenance() {
    currentPage = 'maintenance';
    updateActiveNavigation('maintenance');
    loadMaintenance();
}

function showUsers() {
    if (!auth.isAdmin()) {
        showToast('Access denied. Admin privileges required.', 'error');
        return;
    }
    currentPage = 'users';
    updateActiveNavigation('users');
    loadUsers();
}

// Update active navigation
function updateActiveNavigation(page) {
    // Remove active class from all nav links
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to current page
    const navMap = {
        dashboard: 'a[onclick="showDashboard()"]',
        vehicles: 'a[onclick="showVehicles()"]',
        drivers: 'a[onclick="showDrivers()"]',
        trips: 'a[onclick="showTrips()"]',
        maintenance: 'a[onclick="showMaintenance()"]',
        users: 'a[onclick="showUsers()"]'
    };
    
    const activeLink = document.querySelector(navMap[page]);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// Load page content
function loadPageContent(html) {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = html;
    mainContent.classList.add('fade-in');
}

// Generic table renderer
function renderTable(containerId, data, columns, actions = []) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let tableHtml = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col.header}</th>`).join('')}
                        ${actions.length > 0 ? '<th>Actions</th>' : ''}
                    </tr>
                </thead>
                <tbody>
    `;

    if (data.length === 0) {
        tableHtml += `
            <tr>
                <td colspan="${columns.length + (actions.length > 0 ? 1 : 0)}" class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-2"></i><br>
                    No data available
                </td>
            </tr>
        `;
    } else {
        data.forEach(item => {
            tableHtml += '<tr>';
            columns.forEach(col => {
                let value = item[col.field];
                if (col.formatter) {
                    value = col.formatter(value, item);
                }
                tableHtml += `<td>${value}</td>`;
            });
            
            if (actions.length > 0) {
                tableHtml += '<td>';
                actions.forEach(action => {
                    if (!action.condition || action.condition(item)) {
                        tableHtml += `<button class="btn btn-sm ${action.class}" onclick="${action.onclick}(${item.id})" title="${action.title}">
                            <i class="${action.icon}"></i>
                        </button> `;
                    }
                });
                tableHtml += '</td>';
            }
            
            tableHtml += '</tr>';
        });
    }

    tableHtml += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = tableHtml;
}

// Generic modal functions
function showModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function hideModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

// Generic form handler
function handleFormSubmit(formId, submitHandler) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Convert empty strings to null
        Object.keys(data).forEach(key => {
            if (data[key] === '') {
                data[key] = null;
            }
        });

        await submitHandler(data);
    });
}

// Generic confirmation dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Search functionality
function setupSearch(inputId, searchHandler) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;

    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchHandler(e.target.value);
        }, 300);
    });
}

// Filter functionality
function setupFilters(containerId, filterHandler) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.addEventListener('change', (e) => {
        if (e.target.matches('select, input[type="checkbox"], input[type="radio"]')) {
            const filters = {};
            const formData = new FormData(container);
            
            for (let [key, value] of formData.entries()) {
                if (value) {
                    filters[key] = value;
                }
            }
            
            filterHandler(filters);
        }
    });
}

// Pagination functionality
function renderPagination(containerId, currentPage, totalPages, pageHandler) {
    const container = document.getElementById(containerId);
    if (!container || totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let paginationHtml = '<nav><ul class="pagination justify-content-center">';
    
    // Previous button
    paginationHtml += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="${pageHandler}(${currentPage - 1})">Previous</a>
        </li>
    `;
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="${pageHandler}(1)">1</a></li>`;
        if (startPage > 2) {
            paginationHtml += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHtml += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="${pageHandler}(${i})">${i}</a>
            </li>
        `;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHtml += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="${pageHandler}(${totalPages})">${totalPages}</a></li>`;
    }
    
    // Next button
    paginationHtml += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="${pageHandler}(${currentPage + 1})">Next</a>
        </li>
    `;
    
    paginationHtml += '</ul></nav>';
    container.innerHTML = paginationHtml;
}

// Export functionality
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        showToast('No data to export', 'warning');
        return;
    }

    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => {
            const value = row[header];
            // Escape commas and quotes
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        }).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Print functionality
function printTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>Fleet Management Report</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    @media print { body { margin: 0; } }
                </style>
            </head>
            <body>
                <h1>Fleet Management Report</h1>
                <p>Generated on: ${new Date().toLocaleString()}</p>
                ${table.outerHTML}
            </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeAuth();
    checkAuthStatus();
});

// Handle browser back/forward buttons
window.addEventListener('popstate', (e) => {
    if (e.state && e.state.page) {
        switch (e.state.page) {
            case 'dashboard':
                showDashboard();
                break;
            case 'vehicles':
                showVehicles();
                break;
            case 'drivers':
                showDrivers();
                break;
            case 'trips':
                showTrips();
                break;
            case 'maintenance':
                showMaintenance();
                break;
            case 'users':
                showUsers();
                break;
        }
    }
});

// Update browser history
function updateHistory(page) {
    history.pushState({ page }, '', `#${page}`);
}

