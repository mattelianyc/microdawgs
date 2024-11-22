import { useState, useCallback } from 'react';
import api from '../services/api';

export const useUpload = () => {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [uploadedFile, setUploadedFile] = useState(null);

    const upload = useCallback(async (file) => {
        try {
            setUploading(true);
            setError(null);
            const response = await api.uploadReference(file);
            setUploadedFile(response.data);
            return response.data;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setUploading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setUploading(false);
        setError(null);
        setUploadedFile(null);
    }, []);

    return {
        upload,
        uploading,
        error,
        uploadedFile,
        reset
    };
}; 