// Application State
let currentResourceId = null;
let deleteResourceId = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    loadResources();
    setupEventListeners();
});

function setupEventListeners() {
    // Add Resource Button
    document.getElementById('addResourceBtn').addEventListener('click', showAddResourceModal);
    
    // Add Resource Form
    document.getElementById('addResourceForm').addEventListener('submit', handleAddResource);
}

// Load Resources
async function loadResources() {
    try {
        const response = await api.getResources();
        const resources = response.data;
        
        const resourcesList = document.getElementById('resourcesList');
        const emptyState = document.getElementById('emptyState');
        
        if (resources.length === 0) {
            resourcesList.innerHTML = '';
            emptyState.style.display = 'block';
        } else {
            emptyState.style.display = 'none';
            resourcesList.innerHTML = resources
                .map(resource => createResourceCard(resource))
                .join('');
        }
    } catch (error) {
        console.error('Error loading resources:', error);
        showToast(error.message || 'Ошибка загрузки ресурсов', 'error');
    }
}

// Show Resource Detail
async function showResourceDetail(resourceId) {
    try {
        currentResourceId = resourceId;
        
        // Load resource data
        const [resourceResponse, statusesResponse] = await Promise.all([
            api.getResource(resourceId),
            api.getResourceStatuses(resourceId)
        ]);
        
        const resource = resourceResponse.data;
        const statuses = statusesResponse.data;
        
        // Update UI
        document.getElementById('dashboardView').style.display = 'none';
        document.getElementById('detailView').style.display = 'block';
        
        const detailContainer = document.getElementById('resourceDetail');
        detailContainer.innerHTML = createResourceDetail(resource, statuses);
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        console.error('Error loading resource detail:', error);
        showToast(error.message || 'Ошибка загрузки данных ресурса', 'error');
    }
}

// Show Dashboard
function showDashboard() {
    document.getElementById('detailView').style.display = 'none';
    document.getElementById('dashboardView').style.display = 'block';
    currentResourceId = null;
    loadResources();
}

// Modal Functions
function showAddResourceModal() {
    const modal = document.getElementById('addResourceModal');
    modal.classList.add('show');
    document.getElementById('resourceUrl').focus();
}

function closeModal() {
    const modal = document.getElementById('addResourceModal');
    modal.classList.remove('show');
    document.getElementById('addResourceForm').reset();
    document.getElementById('formError').style.display = 'none';
}

async function handleAddResource(e) {
    e.preventDefault();
    
    const form = e.target;
    const url = form.url.value.trim();
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const formError = document.getElementById('formError');
    
    // Show loading
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    formError.style.display = 'none';
    
    try {
        await api.createResource(url);
        closeModal();
        loadResources();
        showToast('Ресурс успешно добавлен');
    } catch (error) {
        console.error('Error creating resource:', error);
        formError.textContent = error.message || 'Ошибка добавления ресурса';
        formError.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

// Delete Modal Functions
function showDeleteModal(resourceId, resourceUrl) {
    deleteResourceId = resourceId;
    document.getElementById('deleteResourceUrl').textContent = resourceUrl;
    document.getElementById('deleteModal').classList.add('show');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('show');
    deleteResourceId = null;
}

async function confirmDelete() {
    if (!deleteResourceId) return;
    
    try {
        await api.deleteResource(deleteResourceId);
        closeDeleteModal();
        
        if (currentResourceId === deleteResourceId) {
            showDashboard();
        } else {
            loadResources();
        }
        
        showToast('Ресурс успешно удален');
    } catch (error) {
        console.error('Error deleting resource:', error);
        showToast(error.message || 'Ошибка удаления ресурса', 'error');
    }
}

// Auto-refresh
setInterval(() => {
    if (currentResourceId) {
        showResourceDetail(currentResourceId);
    } else {
        loadResources();
    }
}, 30000); // Refresh every 30 seconds
