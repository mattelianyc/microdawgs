import { configureStore } from '@reduxjs/toolkit';
import exampleReducer from './slices/exampleSlice';

const store = configureStore({
  reducer: {
    example: exampleReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store; 