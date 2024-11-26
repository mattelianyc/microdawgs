import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            timeout: 60000,
            withCredentials: false,
            headers: {
                'Accept': 'application/json',
            }
        });
    }

    _handleError(error) {
        if (error.response) {
            const message = error.response.data.detail || error.response.data.message || 'Server error';
            throw new Error(message);
        } else if (error.request) {
            console.error('No response received:', error.request);
            throw new Error('No response from server. Please try again.');
        } else {
            console.error('Request setup error:', error.message);
            throw new Error('Failed to make request. Please check your connection.');
        }
    }
}

export default new ApiService(); 