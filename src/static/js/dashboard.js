// Dashboard Module
let dashboardCharts = {};

async function loadDashboard() {
    const dashboardHtml = `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <h1 class="h3 mb-0">Dashboard</h1>
                    <p class="text-muted">Fleet management overview and analytics</p>
                </div>
            </div>

            <!-- Stats Cards -->
            <div class="row mb-4" id="statsCards">
                <!-- Stats will be loaded here -->
            </div>

            <!-- Charts Row -->
            <div class="row mb-4">
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-gas-pump me-2"></i>Fuel Consumption Trends
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="fuelConsumptionChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-chart-bar me-2"></i>Trips per Vehicle
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="tripsPerVehicleChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-wrench me-2"></i>Maintenance Costs
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="maintenanceCostChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-percentage me-2"></i>Vehicle Utilization
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="vehicleUtilizationChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activities -->
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-clock me-2"></i>Recent Trips
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="recentTrips">
                                <!-- Recent trips will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-tools me-2"></i>Recent Maintenance
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="recentMaintenance">
                                <!-- Recent maintenance will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadPageContent(dashboardHtml);
    await loadDashboardData();
}

async function loadDashboardData() {
    showLoading(true);

    try {
        // Load all dashboard data in parallel
        const [
            statsResponse,
            fuelResponse,
            tripsVehicleResponse,
            maintenanceResponse,
            utilizationResponse,
            recentTripsResponse,
            recentMaintenanceResponse
        ] = await Promise.all([
            api.getDashboardStats(),
            api.getFuelConsumptionTrends(30),
            api.getTripsPerVehicle(),
            api.getMaintenanceCostTrends(6),
            api.getVehicleUtilization(30),
            api.getTrips({ limit: 5 }),
            api.getMaintenance({ limit: 5 })
        ]);

        // Load stats cards
        if (statsResponse.success) {
            loadStatsCards(statsResponse.data.data);
        }

        // Load charts
        if (fuelResponse.success) {
            loadFuelConsumptionChart(fuelResponse.data.data);
        }

        if (tripsVehicleResponse.success) {
            loadTripsPerVehicleChart(tripsVehicleResponse.data.data);
        }

        if (maintenanceResponse.success) {
            loadMaintenanceCostChart(maintenanceResponse.data.data);
        }

        if (utilizationResponse.success) {
            loadVehicleUtilizationChart(utilizationResponse.data.data);
        }

        // Load recent activities
        if (recentTripsResponse.success) {
            loadRecentTrips(recentTripsResponse.data.data);
        }

        if (recentMaintenanceResponse.success) {
            loadRecentMaintenance(recentMaintenanceResponse.data.data);
        }

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error loading dashboard data', 'error');
    } finally {
        showLoading(false);
    }
}

function loadStatsCards(stats) {
    const statsContainer = document.getElementById('statsCards');
    if (!statsContainer) return;

    const statsHtml = `
        <div class="col-lg-3 col-md-6 mb-3">
            <div class="stats-card">
                <div class="stats-icon">
                    <i class="fas fa-car"></i>
                </div>
                <div class="stats-number">${stats.vehicles.total}</div>
                <div class="stats-label">Total Vehicles</div>
                <small>${stats.vehicles.active} Active • ${stats.vehicles.maintenance} Maintenance</small>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
            <div class="stats-card success">
                <div class="stats-icon">
                    <i class="fas fa-users"></i>
                </div>
                <div class="stats-number">${stats.drivers.total}</div>
                <div class="stats-label">Total Drivers</div>
                <small>${stats.drivers.active} Active • ${stats.drivers.inactive} Inactive</small>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
            <div class="stats-card warning">
                <div class="stats-icon">
                    <i class="fas fa-route"></i>
                </div>
                <div class="stats-number">${stats.trips.total}</div>
                <div class="stats-label">Total Trips</div>
                <small>${stats.trips.recent_30_days} in last 30 days</small>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
            <div class="stats-card danger">
                <div class="stats-icon">
                    <i class="fas fa-dollar-sign"></i>
                </div>
                <div class="stats-number">${formatCurrency(stats.totals.recent_maintenance_cost)}</div>
                <div class="stats-label">Maintenance Cost</div>
                <small>Last 30 days</small>
            </div>
        </div>
    `;

    statsContainer.innerHTML = statsHtml;
}

function loadFuelConsumptionChart(data) {
    const ctx = document.getElementById('fuelConsumptionChart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (dashboardCharts.fuelConsumption) {
        dashboardCharts.fuelConsumption.destroy();
    }

    dashboardCharts.fuelConsumption = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Fuel Consumption (L)',
                data: data.values,
                borderColor: 'rgb(37, 99, 235)',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Liters'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

function loadTripsPerVehicleChart(data) {
    const ctx = document.getElementById('tripsPerVehicleChart');
    if (!ctx) return;

    if (dashboardCharts.tripsPerVehicle) {
        dashboardCharts.tripsPerVehicle.destroy();
    }

    dashboardCharts.tripsPerVehicle = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Number of Trips',
                data: data.values,
                backgroundColor: 'rgba(37, 99, 235, 0.8)',
                borderColor: 'rgb(37, 99, 235)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Trips'
                    }
                }
            }
        }
    });
}

function loadMaintenanceCostChart(data) {
    const ctx = document.getElementById('maintenanceCostChart');
    if (!ctx) return;

    if (dashboardCharts.maintenanceCost) {
        dashboardCharts.maintenanceCost.destroy();
    }

    dashboardCharts.maintenanceCost = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Maintenance Cost ($)',
                data: data.values,
                borderColor: 'rgb(245, 158, 11)',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cost ($)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            }
        }
    });
}

function loadVehicleUtilizationChart(data) {
    const ctx = document.getElementById('vehicleUtilizationChart');
    if (!ctx) return;

    if (dashboardCharts.vehicleUtilization) {
        dashboardCharts.vehicleUtilization.destroy();
    }

    const labels = data.map(item => item.vehicle);
    const values = data.map(item => item.utilization_rate);

    dashboardCharts.vehicleUtilization = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(37, 99, 235, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function loadRecentTrips(trips) {
    const container = document.getElementById('recentTrips');
    if (!container) return;

    if (trips.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No recent trips</p>';
        return;
    }

    let html = '<div class="list-group list-group-flush">';
    trips.slice(0, 5).forEach(trip => {
        html += `
            <div class="list-group-item border-0 px-0">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${trip.source} → ${trip.destination}</h6>
                        <p class="mb-1 text-muted small">
                            <i class="fas fa-car me-1"></i>${trip.vehicle ? trip.vehicle.reg_no : 'N/A'}
                            <i class="fas fa-user ms-2 me-1"></i>${trip.driver ? trip.driver.name : 'N/A'}
                        </p>
                        <small class="text-muted">${formatDate(trip.trip_date)}</small>
                    </div>
                    <div class="text-end">
                        ${getStatusBadge(trip.status)}
                        ${trip.distance ? `<br><small class="text-muted">${trip.distance} km</small>` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

function loadRecentMaintenance(maintenance) {
    const container = document.getElementById('recentMaintenance');
    if (!container) return;

    if (maintenance.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No recent maintenance</p>';
        return;
    }

    let html = '<div class="list-group list-group-flush">';
    maintenance.slice(0, 5).forEach(record => {
        html += `
            <div class="list-group-item border-0 px-0">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${record.description}</h6>
                        <p class="mb-1 text-muted small">
                            <i class="fas fa-car me-1"></i>${record.vehicle ? record.vehicle.reg_no : 'N/A'}
                        </p>
                        <small class="text-muted">${formatDate(record.date)}</small>
                    </div>
                    <div class="text-end">
                        ${getStatusBadge(record.maintenance_type)}
                        <br><small class="text-muted">${formatCurrency(record.cost)}</small>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

// Refresh dashboard data
async function refreshDashboard() {
    await loadDashboardData();
    showToast('Dashboard refreshed', 'success');
}

