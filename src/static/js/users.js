// Users Module (Admin only)
let usersData = [];

async function loadUsers() {
    if (!auth.isAdmin()) {
        showToast('Access denied. Admin privileges required.', 'error');
        return;
    }

    const usersHtml = `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 class="h3 mb-0">Users</h1>
                            <p class="text-muted">Manage system users and permissions</p>
                        </div>
                        <div>
                            <button class="btn btn-primary" onclick="showAddUserModal()">
                                <i class="fas fa-plus me-2"></i>Add User
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Users Table -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="usersTable">
                                <!-- Table will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadPageContent(usersHtml);
    await loadUsersData();
}

async function loadUsersData() {
    showLoading(true);
    
    try {
        const response = await api.getUsers();
        if (response.success) {
            usersData = response.data.data;
            renderUsersTable(usersData);
        } else {
            showToast('Error loading users', 'error');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showToast('Error loading users', 'error');
    } finally {
        showLoading(false);
    }
}

function renderUsersTable(users) {
    const columns = [
        { field: 'username', header: 'Username' },
        { field: 'email', header: 'Email' },
        { field: 'role', header: 'Role', formatter: (value) => getStatusBadge(value) },
        { field: 'is_active', header: 'Status', formatter: (value) => getStatusBadge(value ? 'active' : 'inactive') },
        { field: 'created_at', header: 'Created', formatter: (value) => formatDate(value) }
    ];

    const actions = [
        { icon: 'fas fa-edit', class: 'btn-outline-primary', onclick: 'editUser', title: 'Edit' },
        { 
            icon: 'fas fa-trash', 
            class: 'btn-outline-danger', 
            onclick: 'deleteUser', 
            title: 'Delete',
            condition: (item) => item.id !== auth.getUser().id // Can't delete self
        }
    ];

    renderTable('usersTable', users, columns, actions);
}

function showAddUserModal() {
    showToast('User management coming soon!', 'info');
}

function editUser(id) {
    showToast('User editing coming soon!', 'info');
}

function deleteUser(id) {
    showToast('User deletion coming soon!', 'info');
}

