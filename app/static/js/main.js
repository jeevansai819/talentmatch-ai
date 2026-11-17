// TalentMatch AI - Core JavaScript Utilities
const API_BASE = '/api';

// Toast Notifications
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `<span style="font-weight:bold">${icon}</span> <span>${message}</span>`;
    
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Token Storage & Authentication
function getAuthToken() {
    return localStorage.getItem('talentmatch_token') || getCookie('access_token');
}

function setAuthToken(token) {
    localStorage.setItem('talentmatch_token', token);
    document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;
}

function removeAuthToken() {
    localStorage.removeItem('talentmatch_token');
    document.cookie = 'access_token=; path=/; max-age=0';
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Authenticated Fetch wrapper
async function authFetch(url, options = {}) {
    const token = getAuthToken();
    const headers = options.headers || {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(url, { ...options, headers });
    if (res.status === 401 && !url.includes('/login')) {
        removeAuthToken();
        window.location.href = '/login?expired=1';
    }
    return res;
}

// Logout handler
function handleLogout() {
    removeAuthToken();
    showToast('Logged out successfully.', 'info');
    setTimeout(() => {
        window.location.href = '/login';
    }, 400);
}

// Modal Helpers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Close modals on clicking backdrop
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
});
