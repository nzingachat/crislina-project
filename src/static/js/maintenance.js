// Maintenance Module
let maintenanceData = [];

async function loadMaintenance() {
    const maintenanceHtml = `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 class="h3 mb-0">Maintenance</h1>
                            <p class="text-muted">Manage vehicle maintenance records</p>
                        </div>
                        <div>
                            ${auth.canManage() ? '<button class="btn btn-primary" onclick="showAddMaintenanceModal()"><i class="fas fa-plus me-2"></i>Add Record</button>' : ''}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Maintenance Table -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="maintenanceTable">
                                <!-- Table will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadPageContent(maintenanceHtml);
    await loadMaintenanceData();
}

async function loadMaintenanceData() {
    showLoading(true);
    
    try {
        const response = await api.getMaintenance();
        if (response.success) {
            maintenanceData = response.data.data;
            renderMaintenanceTable(maintenanceData);
        } else {
            showToast('Error loading maintenance records', 'error');
        }
    } catch (error) {
        console.error('Error loading maintenance:', error);
        showToast('Error loading maintenance records', 'error');
    } finally {
        showLoading(false);
    }
}

function renderMaintenanceTable(maintenance) {
    const columns = [
        { field: 'vehicle', header: 'Vehicle', formatter: (value) => value ? value.reg_no : 'N/A' },
        { field: 'description', header: 'Description' },
        { field: 'maintenance_type', header: 'Type', formatter: (value) => getStatusBadge(value) },
        { field: 'cost', header: 'Cost', formatter: (value) => formatCurrency(value) },
        { field: 'date', header: 'Date', formatter: (value) => formatDate(value) },
        { field: 'status', header: 'Status', formatter: (value) => getStatusBadge(value) }
    ];

    const actions = [];
    
    if (auth.canManage()) {
        actions.push(
            { icon: 'fas fa-edit', class: 'btn-outline-primary', onclick: 'editMaintenance', title: 'Edit' },
            { icon: 'fas fa-trash', class: 'btn-outline-danger', onclick: 'deleteMaintenance', title: 'Delete', condition: (item) => auth.isAdmin() }
        );
    }

    renderTable('maintenanceTable', maintenance, columns, actions);
}

function showAddMaintenanceModal() {
    showToast('Maintenance management coming soon!', 'info');
}

function editMaintenance(id) {
    showToast('Maintenance editing coming soon!', 'info');
}

function deleteMaintenance(id) {
    showToast('Maintenance deletion coming soon!', 'info');
}

