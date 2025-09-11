// Trips Module
let tripsData = [];

async function loadTrips() {
    const tripsHtml = `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 class="h3 mb-0">Trips</h1>
                            <p class="text-muted">Manage fleet trips and routes</p>
                        </div>
                        <div>
                            ${auth.canManage() ? '<button class="btn btn-primary" onclick="showAddTripModal()"><i class="fas fa-plus me-2"></i>Add Trip</button>' : ''}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Trips Table -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="tripsTable">
                                <!-- Table will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadPageContent(tripsHtml);
    await loadTripsData();
}

async function loadTripsData() {
    showLoading(true);
    
    try {
        const response = await api.getTrips();
        if (response.success) {
            tripsData = response.data.data;
            renderTripsTable(tripsData);
        } else {
            showToast('Error loading trips', 'error');
        }
    } catch (error) {
        console.error('Error loading trips:', error);
        showToast('Error loading trips', 'error');
    } finally {
        showLoading(false);
    }
}

function renderTripsTable(trips) {
    const columns = [
        { field: 'source', header: 'Source' },
        { field: 'destination', header: 'Destination' },
        { field: 'vehicle', header: 'Vehicle', formatter: (value) => value ? value.reg_no : 'N/A' },
        { field: 'driver', header: 'Driver', formatter: (value) => value ? value.name : 'N/A' },
        { field: 'distance', header: 'Distance (km)', formatter: (value) => value ? formatNumber(value) : 'N/A' },
        { field: 'status', header: 'Status', formatter: (value) => getStatusBadge(value) },
        { field: 'trip_date', header: 'Date', formatter: (value) => formatDate(value) }
    ];

    const actions = [];
    
    if (auth.canManage()) {
        actions.push(
            { icon: 'fas fa-edit', class: 'btn-outline-primary', onclick: 'editTrip', title: 'Edit' },
            { icon: 'fas fa-trash', class: 'btn-outline-danger', onclick: 'deleteTrip', title: 'Delete', condition: (item) => auth.isAdmin() }
        );
    }

    renderTable('tripsTable', trips, columns, actions);
}

function showAddTripModal() {
    showToast('Trip management coming soon!', 'info');
}

function editTrip(id) {
    showToast('Trip editing coming soon!', 'info');
}

function deleteTrip(id) {
    showToast('Trip deletion coming soon!', 'info');
}

