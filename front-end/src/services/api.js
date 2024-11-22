import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

class ApiService {
    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Add auth token if available
        this.client.interceptors.request.use(config => {
            const token = localStorage.getItem('auth_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
    }

    async generateImage(params) {
        try {
            const response = await this.client.post('/api/v1/generate', params);
            return response.data;
        } catch (error) {
            this._handleError(error);
        }
    }

    async generateBatch(params) {
        try {
            const response = await this.client.post('/api/v1/batch', params);
            return response.data;
        } catch (error) {
            this._handleError(error);
        }
    }

    async uploadReference(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await this.client.post('/api/v1/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            return response.data;
        } catch (error) {
            this._handleError(error);
        }
    }

    async getBatchStatus(jobId) {
        try {
            const response = await this.client.get(`/api/v1/batch/${jobId}`);
            return response.data;
        } catch (error) {
            this._handleError(error);
        }
    }

    _handleError(error) {
        if (error.response) {
            // Server responded with error
            throw new Error(error.response.data.message || 'Server error');
        } else if (error.request) {
            // Request made but no response
            throw new Error('No response from server');
        } else {
            // Request setup error
            throw new Error('Failed to make request');
        }
    }
}

export default new ApiService(); 