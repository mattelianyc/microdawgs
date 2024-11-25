import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const generateIcon = createAsyncThunk(
  'imageGeneration/generateIcon',
  async ({ prompt, num_steps = 20, guidance_scale = 7.5 }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('num_steps', num_steps);
      formData.append('guidance_scale', guidance_scale);

      const response = await api.client.post('/generate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      const imageUrl = URL.createObjectURL(response.data);
      return imageUrl;
    } catch (error) {
      console.error('Generation error:', error);
      return rejectWithValue(
        error.response?.data?.detail || 
        'Failed to generate icon. Please try again.'
      );
    }
  }
);

const imageGenerationSlice = createSlice({
  name: 'imageGeneration',
  initialState: {
    generatedImage: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearGeneratedImage: (state) => {
      state.generatedImage = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateIcon.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateIcon.fulfilled, (state, action) => {
        state.loading = false;
        state.generatedImage = action.payload;
      })
      .addCase(generateIcon.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearGeneratedImage } = imageGenerationSlice.actions;
export default imageGenerationSlice.reducer; 