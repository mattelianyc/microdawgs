import api from './api';

export const trainingService = {
  uploadTrainingData: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('num_epochs', '100');

    try {
      const response = await api.client.post('/train', 
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
      throw error.response?.data?.detail || 'Training failed';
    }
  }
}; 