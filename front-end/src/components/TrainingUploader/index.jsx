import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { trainingService } from '../../services/trainingService';

const TrainingUploader = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = (acceptedFiles) => {
    const droppedFile = acceptedFiles[0];
    if (droppedFile?.type === 'application/zip') {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please upload a ZIP file');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip']
    },
    maxSize: 100 * 1024 * 1024,
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const result = await trainingService.uploadTrainingData(file, setUploadProgress);
      setStatus(result.data);
    } catch (err) {
      setError(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="training-uploader">
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <i className="upload-icon">📁</i>
          <p>Drag and drop a ZIP file here or click to select</p>
          <p className="dropzone-hint">
            The ZIP file should contain your icon images (.png, .jpg, .jpeg)
          </p>
        </div>
      </div>

      {file && (
        <p className="selected-file">Selected file: {file.name}</p>
      )}

      {uploading && (
        <div className="progress-container">
          <div 
            className="progress-bar" 
            style={{ width: `${uploadProgress}%` }} 
          />
          <p className="progress-text">Uploading... {uploadProgress}%</p>
        </div>
      )}

      {error && (
        <div className="error-message">{error}</div>
      )}

      {status && (
        <div className="success-message">
          Successfully processed {status.processed_images} images!
          <br />
          Training data saved to: {status.training_dir}
        </div>
      )}

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? 'Uploading...' : 'Upload and Train'}
      </button>
    </div>
  );
};

export default TrainingUploader; 