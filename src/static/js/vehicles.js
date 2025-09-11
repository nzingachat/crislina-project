// Vehicles Module
let vehiclesData = [];

async function loadVehicles() {
    const vehiclesHtml = `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 class="h3 mb-0">Vehicles</h1>
                            <p class="text-muted">Manage your fleet vehicles</p>
                        </div>
                        <div>
                            ${auth.canManage() ? '<button class="btn btn-primary" onclick="showAddVehicleModal()"><i class="fas fa-plus me-2"></i>Add Vehicle</button>' : ''}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <label for="statusFilter" class="form-label">Status</label>
                                    <select class="form-select" id="statusFilter" onchange="filterVehicles()">
                                        <option value="">All Statuses</option>
                                        <option value="active">Active</option>
                                        <option value="maintenance">Maintenance</option>
                                        <option value="inactive">Inactive</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label for="fuelTypeFilter" class="form-label">Fuel Type</label>
                                    <select class="form-select" id="fuelTypeFilter" onchange="filterVehicles()">
                                        <option value="">All Fuel Types</option>
                                        <option value="petrol">Petrol</option>
                                        <option value="diesel">Diesel</option>
                                        <option value="electric">Electric</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label for="vehicleSearch" class="form-label">Search</label>
                                    <input type="text" class="form-control" id="vehicleSearch" placeholder="Search vehicles..." onkeyup="searchVehicles()">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Vehicles Table -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="vehiclesTable"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add/Edit Vehicle Modal -->
        <div class="modal fade" id="vehicleModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="vehicleModalTitle">Add Vehicle</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="vehicleForm">
                        <div class="modal-body">
                            <input type="hidden" id="vehicleId">
                            <div class="mb-3">
                                <label for="regNo" class="form-label">Registration Number *</label>
                                <input type="text" class="form-control" id="regNo" required>
                            </div>
                            <div class="mb-3">
                                <label for="model" class="form-label">Model *</label>
                                <input type="text" class="form-control" id="model" required>
                            </div>
                            <div class="mb-3">
                                <label for="fuelType" class="form-label">Fuel Type *</label>
                                <select class="form-select" id="fuelType" required>
                                    <option value="">Select Fuel Type</option>
                                    <option value="petrol">Petrol</option>
                                    <option value="diesel">Diesel</option>
                                    <option value="electric">Electric</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="status" class="form-label">Status</label>
                                <select class="form-select" id="status">
                                    <option value="active">Active</option>
                                    <option value="maintenance">Maintenance</option>
                                    <option value="inactive">Inactive</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Vehicle</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;

    loadPageContent(vehiclesHtml);
    await loadVehiclesData();
    setupVehicleForm();
}

// Modal Helpers using Bootstrap API
function showModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalEl, { backdrop: 'static', keyboard: true });
    modal.show();
}

function hideModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
}

// --- Rest of your code (loadVehiclesData, renderVehiclesTable, filterVehicles, searchVehicles, editVehicle, deleteVehicle, setupVehicleForm) remains the same ---


async function loadVehiclesData() {
    showLoading(true);
    
    try {
        const response = await api.getVehicles();
        if (response.success) {
            vehiclesData = response.data.data;
            renderVehiclesTable(vehiclesData);
        } else {
            showToast('Error loading vehicles', 'error');
        }
    } catch (error) {
        console.error('Error loading vehicles:', error);
        showToast('Error loading vehicles', 'error');
    } finally {
        showLoading(false);
    }
}

function renderVehiclesTable(vehicles) {
    const columns = [
        { field: 'reg_no', header: 'Registration' },
        { field: 'model', header: 'Model' },
        { field: 'fuel_type', header: 'Fuel Type', formatter: (value) => value.charAt(0).toUpperCase() + value.slice(1) },
        { field: 'status', header: 'Status', formatter: (value) => getStatusBadge(value) },
        { field: 'created_at', header: 'Created', formatter: (value) => formatDate(value) }
    ];

    const actions = [];
    
    if (auth.canManage()) {
        actions.push(
            { icon: 'fas fa-edit', class: 'btn-outline-primary', onclick: 'editVehicle', title: 'Edit' },
            { icon: 'fas fa-trash', class: 'btn-outline-danger', onclick: 'deleteVehicle', title: 'Delete', condition: (item) => auth.isAdmin() }
        );
    }

    renderTable('vehiclesTable', vehicles, columns, actions);
}

function filterVehicles() {
    const statusFilter = document.getElementById('statusFilter').value;
    const fuelTypeFilter = document.getElementById('fuelTypeFilter').value;
    
    let filtered = vehiclesData;
    
    if (statusFilter) {
        filtered = filtered.filter(v => v.status === statusFilter);
    }
    
    if (fuelTypeFilter) {
        filtered = filtered.filter(v => v.fuel_type === fuelTypeFilter);
    }
    
    renderVehiclesTable(filtered);
}

function searchVehicles() {
    const searchTerm = document.getElementById('vehicleSearch').value.toLowerCase();
    
    if (!searchTerm) {
        renderVehiclesTable(vehiclesData);
        return;
    }
    
    const filtered = vehiclesData.filter(v => 
        v.reg_no.toLowerCase().includes(searchTerm) ||
        v.model.toLowerCase().includes(searchTerm)
    );
    
    renderVehiclesTable(filtered);
}

function showAddVehicleModal() {
    document.getElementById('vehicleModalTitle').textContent = 'Add Vehicle';
    document.getElementById('vehicleForm').reset();
    document.getElementById('vehicleId').value = '';
    showModal('vehicleModal');
}

function editVehicle(id) {
    const vehicle = vehiclesData.find(v => v.id === id);
    if (!vehicle) return;
    
    document.getElementById('vehicleModalTitle').textContent = 'Edit Vehicle';
    document.getElementById('vehicleId').value = vehicle.id;
    document.getElementById('regNo').value = vehicle.reg_no;
    document.getElementById('model').value = vehicle.model;
    document.getElementById('fuelType').value = vehicle.fuel_type;
    document.getElementById('status').value = vehicle.status;
    
    showModal('vehicleModal');
}

async function deleteVehicle(id) {
    const vehicle = vehiclesData.find(v => v.id === id);
    if (!vehicle) return;
    
    if (confirm(`Are you sure you want to delete vehicle ${vehicle.reg_no}?`)) {
        showLoading(true);
        
        try {
            const response = await api.deleteVehicle(id);
            if (response.success) {
                showToast('Vehicle deleted successfully', 'success');
                await loadVehiclesData();
            } else {
                showToast(response.data.message || 'Error deleting vehicle', 'error');
            }
        } catch (error) {
            console.error('Error deleting vehicle:', error);
            showToast('Error deleting vehicle', 'error');
        } finally {
            showLoading(false);
        }
    }
}

function setupVehicleForm() {
    const form = document.getElementById('vehicleForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const vehicleId = document.getElementById('vehicleId').value;
        const vehicleData = {
            reg_no: document.getElementById('regNo').value,
            model: document.getElementById('model').value,
            fuel_type: document.getElementById('fuelType').value,
            status: document.getElementById('status').value
        };
        
        showLoading(true);
        
        try {
            let response;
            if (vehicleId) {
                response = await api.updateVehicle(vehicleId, vehicleData);
            } else {
                response = await api.createVehicle(vehicleData);
            }
            
            if (response.success) {
                showToast(`Vehicle ${vehicleId ? 'updated' : 'created'} successfully`, 'success');
                hideModal('vehicleModal');
                await loadVehiclesData();
            } else {
                showToast(response.data.message || `Error ${vehicleId ? 'updating' : 'creating'} vehicle`, 'error');
            }
        } catch (error) {
            console.error('Error saving vehicle:', error);
            showToast('Error saving vehicle', 'error');
        } finally {
            showLoading(false);
        }
    });
}

