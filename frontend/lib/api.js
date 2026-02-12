// API client utilities for JWT handling
// Note: Using localStorage-based auth instead of Better Auth client for now
// since the current auth system stores user data in localStorage

class ApiClient {
  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  // Get JWT token from localStorage (where it should be stored after login)
  async getAuthToken() {
    // Try to get token from localStorage
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    return token;
  }

  // Create headers with JWT token
  async getAuthHeaders() {
    const token = await this.getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = await this.getAuthHeaders();

    const config = {
      headers: {
        ...headers,
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      // Don't throw error immediately, just return response info
      // This allows the calling function to handle different status codes appropriately
      const errorText = await response.text();
      console.error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    return response.json();
  }

  // GET request
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // PUT request
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // PATCH request
  async patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Create a singleton instance
const apiClient = new ApiClient();

export default apiClient;