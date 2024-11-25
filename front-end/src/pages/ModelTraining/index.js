import React from 'react';
import TrainingUploader from '../../components/TrainingUploader';
import './styles.scss';

const ModelTraining = () => {
  return (
    <div className="model-training-page">
      <h1>Train Model with Custom Icons</h1>
      <TrainingUploader />
    </div>
  );
};

export default ModelTraining; 