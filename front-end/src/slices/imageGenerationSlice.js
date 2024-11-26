import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const generateIcon = createAsyncThunk(
  'imageGeneration/generateIcon',
  async (promptData, { dispatch }) => {
    try {
      dispatch(setLoading(true));
      
      const formData = new FormData();
      formData.append('prompt', promptData.prompt);
      formData.append('num_steps', '20');
      formData.append('guidance_scale', '7.5');

      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to generate icon');
      }

      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      return imageUrl;
    } catch (error) {
      throw error;
    }
  }
);

const imageGenerationSlice = createSlice({
  name: 'imageGeneration',
  initialState: {
    loading: false,
    error: null,
    generatedImage: null,
    progress: 0,
    progressMessage: ''
  },
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
      if (!action.payload) {
        state.progress = 0;
        state.progressMessage = '';
      }
    },
    setProgress: (state, action) => {
      state.progress = action.payload.progress;
      state.progressMessage = action.payload.message;
    },
    clearState: (state) => {
      state.loading = false;
      state.error = null;
      state.generatedImage = null;
      state.progress = 0;
      state.progressMessage = '';
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateIcon.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.progress = 0;
        state.progressMessage = 'Starting generation...';
      })
      .addCase(generateIcon.fulfilled, (state, action) => {
        state.loading = false;
        state.generatedImage = action.payload;
        state.progress = 100;
        state.progressMessage = 'Generation complete!';
      })
      .addCase(generateIcon.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.progress = 0;
        state.progressMessage = '';
      });
  },
});

export const { setLoading, setProgress, clearState } = imageGenerationSlice.actions;
export default imageGenerationSlice.reducer; 