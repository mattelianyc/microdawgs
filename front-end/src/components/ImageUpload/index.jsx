import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './styles.css';

const ImageUpload = ({ onUpload, maxSize = 10485760 }) => {
    const [preview, setPreview] = useState(null);
    const [error, setError] = useState(null);

    const onDrop = useCallback(acceptedFiles => {
        const file = acceptedFiles[0];
        
        if (!file) {
            return;
        }

        // Validate file size
        if (file.size > maxSize) {
            setError(`File too large. Maximum size is ${maxSize / 1024 / 1024}MB`);
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onloadend = () => {
            setPreview(reader.result);
        };
        reader.readAsDataURL(file);

        // Pass file to parent
        onUpload(file);
        setError(null);
    }, [maxSize, onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        },
        maxSize,
        multiple: false
    });

    return (
        <div className="image-upload-container">
            <div 
                {...getRootProps()} 
                className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
                <input {...getInputProps()} />
                {preview ? (
                    <img 
                        src={preview} 
                        alt="Preview" 
                        className="preview-image"
                    />
                ) : (
                    <p>Drag & drop an image here, or click to select</p>
                )}
            </div>
            {error && <p className="error-message">{error}</p>}
        </div>
    );
};

export default ImageUpload; 