// ============================================================================
// FRONTEND AUTHENTICATION MODULE
// ============================================================================

/**
 * Authentication utilities for managing user sessions and API calls
 */

const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000';
window.API_BASE_URL = API_BASE_URL;

const Auth = {
  /**
   * Get the stored JWT token
   */
  getToken() {
    return localStorage.getItem('auth_token');
  },

  /**
   * Get the stored user object
   */
  getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getToken();
  },

  /**
   * Save authentication data
   */
  setAuth(token, user) {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },

  /**
   * Clear authentication data
   */
  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
  },

  /**
   * Make authenticated API call
   */
  async apiCall(url, options = {}) {
    const token = this.getToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      // If unauthorized, redirect to login
      if (response.status === 401) {
        this.logout();
        return null;
      }

      return response;
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  },

  /**
   * Make authenticated GET request
   */
  async get(url) {
    return this.apiCall(url, { method: 'GET' });
  },

  /**
   * Make authenticated POST request
   */
  async post(url, data) {
    return this.apiCall(url, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Make authenticated PUT request
   */
  async put(url, data) {
    return this.apiCall(url, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  /**
   * Ensure user is authenticated
   */
  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  /**
   * Update user info in localStorage
   */
  async refreshUser() {
    try {
      const response = await this.get(`${API_BASE_URL}/api/auth/me`);
      if (response && response.ok) {
        const data = await response.json();
        localStorage.setItem('user', JSON.stringify(data.data));
        return data.data;
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
    return null;
  }
};

window.Auth = Auth;

// ============================================================================
// PAGE PROTECTION
// ============================================================================

/**
 * Protect a page - redirect to login if not authenticated
 */
function protectPage() {
  if (!Auth.isAuthenticated()) {
    window.location.href = 'login.html';
  }
}

/**
 * Unprotect a page - redirect to dashboard if already authenticated
 */
function unprotectPage() {
  if (Auth.isAuthenticated()) {
    window.location.href = 'dashboard.html';
  }
}

// ============================================================================
// UI HELPERS
// ============================================================================

/**
 * Update navbar with user info
 */
function updateNavbarUser() {
  const user = Auth.getUser();
  if (!user) return;

  // Update Account button if exists
  const accountBtn = document.querySelector('.btn-outline:last-child');
  if (accountBtn && accountBtn.textContent === 'Account') {
    accountBtn.textContent = user.username || user.email;
    accountBtn.onclick = () => {
      // Show user menu or profile
      console.log('Show user menu');
    };
  }
}

/**
 * Add logout functionality to a button
 */
function addLogoutListener(selector) {
  const element = document.querySelector(selector);
  if (element) {
    element.addEventListener('click', () => {
      if (confirm('Are you sure you want to logout?')) {
        Auth.logout();
      }
    });
  }
}

/**
 * Show user profile in sidebar or header
 */
function showUserProfile() {
  const user = Auth.getUser();
  if (!user) return;

  const profileElements = document.querySelectorAll('.sidebar-user-name');
  profileElements.forEach(el => {
    el.textContent = user.username || user.full_name || 'User';
  });

  const emailElements = document.querySelectorAll('.sidebar-user-role');
  emailElements.forEach(el => {
    el.textContent = user.email || 'Pro Plan';
  });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Update navbar when page loads
  updateNavbarUser();
  showUserProfile();

  // Add console log for debugging
  const user = Auth.getUser();
  if (user) {
    console.log('✓ User authenticated:', user.username);
  }
});
