import { configureStore } from '@reduxjs/toolkit';
import exampleReducer from './slices/exampleSlice';
import imageGenerationReducer from './slices/imageGenerationSlice';

const store = configureStore({
  reducer: {
    example: exampleReducer,
    imageGeneration: imageGenerationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store; 