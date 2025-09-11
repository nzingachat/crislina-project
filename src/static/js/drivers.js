// Drivers Module
let driversData = [];

async function loadDrivers() {
    const driversHtml = `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 class="h3 mb-0">Drivers</h1>
                            <p class="text-muted">Manage your fleet drivers</p>
                        </div>
                        <div>
                            ${auth.canManage() ? '<button class="btn btn-primary" onclick="showAddDriverModal()"><i class="fas fa-plus me-2"></i>Add Driver</button>' : ''}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Drivers Table -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="driversTable">
                                <!-- Table will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadPageContent(driversHtml);
    await loadDriversData();
}

async function loadDriversData() {
    showLoading(true);
    
    try {
        const response = await api.getDrivers();
        if (response.success) {
            driversData = response.data.data;
            renderDriversTable(driversData);
        } else {
            showToast('Error loading drivers', 'error');
        }
    } catch (error) {
        console.error('Error loading drivers:', error);
        showToast('Error loading drivers', 'error');
    } finally {
        showLoading(false);
    }
}

function renderDriversTable(drivers) {
    const columns = [
        { field: 'name', header: 'Name' },
        { field: 'license_no', header: 'License Number' },
        { field: 'phone', header: 'Phone' },
        { field: 'email', header: 'Email' },
        { field: 'status', header: 'Status', formatter: (value) => getStatusBadge(value) }
    ];

    const actions = [];
    
    if (auth.canManage()) {
        actions.push(
            { icon: 'fas fa-edit', class: 'btn-outline-primary', onclick: 'editDriver', title: 'Edit' },
            { icon: 'fas fa-trash', class: 'btn-outline-danger', onclick: 'deleteDriver', title: 'Delete', condition: (item) => auth.isAdmin() }
        );
    }

    renderTable('driversTable', drivers, columns, actions);
}

function showAddDriverModal() {
    showToast('Driver management coming soon!', 'info');
}

function editDriver(id) {
    showToast('Driver editing coming soon!', 'info');
}

function deleteDriver(id) {
    showToast('Driver deletion coming soon!', 'info');
}

