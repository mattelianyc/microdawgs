import api from './api';

export const trainingService = {
  uploadTrainingData: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.client.post('/api/generate/upload-training-data', 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const progress = (progressEvent.loaded / progressEvent.total) * 100;
            onProgress?.(Math.round(progress));
          }
        }
      );
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Upload failed';
    }
  }
}; 