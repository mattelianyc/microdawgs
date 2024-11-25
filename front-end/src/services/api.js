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

        console.log('API Base URL:', API_BASE_URL);
    }

    _handleError(error) {
        if (error.response) {
            // Server responded with error
            const message = error.response.data.detail || error.response.data.message || 'Server error';
            throw new Error(message);
        } else if (error.request) {
            // Request made but no response
            console.error('No response received:', error.request);
            throw new Error('No response from server. Please try again.');
        } else {
            // Request setup error
            console.error('Request setup error:', error.message);
            throw new Error('Failed to make request. Please check your connection.');
        }
    }
}

export default new ApiService(); 