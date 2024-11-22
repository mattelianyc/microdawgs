import { useState, useCallback } from 'react';
import api from '../services/api';

export const useImageGeneration = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    const generateImage = useCallback(async (params) => {
        try {
            setLoading(true);
            setError(null);
            const response = await api.generateImage(params);
            setResult(response.data);
            return response.data;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setLoading(false);
        setError(null);
        setResult(null);
    }, []);

    return {
        generateImage,
        loading,
        error,
        result,
        reset
    };
}; 