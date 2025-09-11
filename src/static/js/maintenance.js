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

            <!-- Filters & Search -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <label for="statusFilter" class="form-label">Status</label>
                                    <select class="form-select" id="statusFilter" onchange="filterMaintenance()">
                                        <option value="">All Statuses</option>
                                        <option value="active">Active</option>
                                        <option value="completed">Completed</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label for="typeFilter" class="form-label">Maintenance Type</label>
                                    <select class="form-select" id="typeFilter" onchange="filterMaintenance()">
                                        <option value="">All Types</option>
                                        <option value="scheduled">Scheduled</option>
                                        <option value="unscheduled">Unscheduled</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label for="maintenanceSearch" class="form-label">Search</label>
                                    <input type="text" class="form-control" id="maintenanceSearch" placeholder="Search by vehicle or description..." onkeyup="searchMaintenance()">
                                </div>
                            </div>
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
        <!-- Add/Edit Maintenance Modal -->
        <div class="modal fade" id="maintenanceModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="maintenanceModalTitle">Add Maintenance</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="maintenanceForm">
                        <div class="modal-body">
                            <input type="hidden" id="maintenanceId">
                            <div class="mb-3">
                                <label for="vehicleId" class="form-label">Vehicle *</label>
                                <select class="form-select" id="vehicleId" required>
                                    <option value="">Select Vehicle</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="description" class="form-label">Description *</label>
                                <input type="text" class="form-control" id="description" required>
                            </div>
                            <div class="mb-3">
                                <label for="maintenanceType" class="form-label">Type *</label>
                                <select class="form-select" id="maintenanceType" required>
                                    <option value="scheduled">Scheduled</option>
                                    <option value="unscheduled">Unscheduled</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="cost" class="form-label">Cost *</label>
                                <input type="number" class="form-control" id="cost" required>
                            </div>
                            <div class="mb-3">
                                <label for="date" class="form-label">Date *</label>
                                <input type="date" class="form-control" id="date" required>
                            </div>
                            <div class="mb-3">
                                <label for="status" class="form-label">Status *</label>
                                <select class="form-select" id="status">
                                    <option value="active">Active</option>
                                    <option value="completed">Completed</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Record</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;

    loadPageContent(maintenanceHtml);
    await loadMaintenanceData();
    setupMaintenanceForm();
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

// function showAddMaintenanceModal() {
//     showToast('Maintenance management coming soon!', 'info');
// }

// function editMaintenance(id) {
//     showToast('Maintenance editing coming soon!', 'info');
// }

// function deleteMaintenance(id) {
//     showToast('Maintenance deletion coming soon!', 'info');
// }

// Show Add Maintenance Modal
function showAddMaintenanceModal() {
    document.getElementById('maintenanceModalTitle').textContent = 'Add Maintenance';
    document.getElementById('maintenanceForm').reset();
    document.getElementById('maintenanceId').value = '';

    // Load vehicle options dynamically
    api.getVehicles().then(res => {
        if (res.success) {
            const select = document.getElementById('vehicleId');
            select.innerHTML = '<option value="">Select Vehicle</option>';
            res.data.data.forEach(v => {
                select.innerHTML += `<option value="${v.id}">${v.reg_no} (${v.model})</option>`;
            });
        }
    });

    showModal('maintenanceModal');
}

// Edit Maintenance Record
function editMaintenance(id) {
    const record = maintenanceData.find(m => m.id === id);
    if (!record) return;

    document.getElementById('maintenanceModalTitle').textContent = 'Edit Maintenance';
    document.getElementById('maintenanceId').value = record.id;
    document.getElementById('vehicleId').value = record.vehicle_id;
    document.getElementById('description').value = record.description;
    document.getElementById('maintenanceType').value = record.maintenance_type;
    document.getElementById('cost').value = record.cost;
    document.getElementById('date').value = record.date;
    document.getElementById('status').value = record.status;

    showModal('maintenanceModal');
}

// Delete Maintenance Record
async function deleteMaintenance(id) {
    const record = maintenanceData.find(m => m.id === id);
    if (!record) return;

    if (confirm(`Are you sure you want to delete this maintenance record for vehicle ${record.vehicle.reg_no}?`)) {
        showLoading(true);
        try {
            const response = await api.deleteMaintenance(id);
            if (response.success) {
                showToast('Maintenance record deleted successfully', 'success');
                await loadMaintenanceData();
            } else {
                showToast(response.data.message || 'Error deleting maintenance record', 'error');
            }
        } catch (error) {
            console.error('Error deleting maintenance:', error);
            showToast('Error deleting maintenance record', 'error');
        } finally {
            showLoading(false);
        }
    }
}

// Setup Maintenance Form
function setupMaintenanceForm() {
    const form = document.getElementById('maintenanceForm');
    if (!form) return;

    form.addEventListener('submit', async e => {
        e.preventDefault();

        const id = document.getElementById('maintenanceId').value;
        const data = {
            vehicle_id: document.getElementById('vehicleId').value,
            description: document.getElementById('description').value,
            maintenance_type: document.getElementById('maintenanceType').value,
            cost: document.getElementById('cost').value,
            date: document.getElementById('date').value,
            status: document.getElementById('status').value
        };

        showLoading(true);
        try {
            let response;
            if (id) {
                response = await api.updateMaintenance(id, data);
            } else {
                response = await api.createMaintenance(data);
            }

            if (response.success) {
                showToast(`Maintenance record ${id ? 'updated' : 'created'} successfully`, 'success');
                hideModal('maintenanceModal');
                await loadMaintenanceData();
            } else {
                showToast(response.data.message || 'Error saving maintenance record', 'error');
            }
        } catch (error) {
            console.error('Error saving maintenance:', error);
            showToast('Error saving maintenance record', 'error');
        } finally {
            showLoading(false);
        }
    });
}


// Filter Maintenance
function filterMaintenance() {
    const status = document.getElementById('statusFilter').value;
    const type = document.getElementById('typeFilter').value;

    let filtered = maintenanceData;

    if (status) filtered = filtered.filter(m => m.status === status);
    if (type) filtered = filtered.filter(m => m.maintenance_type === type);

    renderMaintenanceTable(filtered);
}

// Search Maintenance
function searchMaintenance() {
    const term = document.getElementById('maintenanceSearch').value.toLowerCase();
    if (!term) {
        renderMaintenanceTable(maintenanceData);
        return;
    }

    const filtered = maintenanceData.filter(m =>
        (m.vehicle && m.vehicle.reg_no.toLowerCase().includes(term)) ||
        (m.description && m.description.toLowerCase().includes(term))
    );

    renderMaintenanceTable(filtered);
}