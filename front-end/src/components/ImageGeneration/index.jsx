import React, { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { generateIcon, setProgress } from '../../slices/imageGenerationSlice';
import PromptInput from '../PromptInput';
import './styles.scss';

const ImageGeneration = () => {
    const dispatch = useDispatch();
    const { loading, error, generatedImage, progress, progressMessage } = useSelector(state => state.imageGeneration);
    const progressInterval = useRef(null);

    // Poll for progress updates
    useEffect(() => {
        const pollProgress = async () => {
            try {
                const response = await fetch('http://localhost:8000/generate/progress');
                const data = await response.json();
                
                console.log('Progress update:', data); // Debug log
                
                dispatch(setProgress({
                    progress: data.progress || 0,
                    message: data.message || 'Generating...'
                }));
                
                if (data.progress >= 100) {
                    clearInterval(progressInterval.current);
                }
            } catch (err) {
                console.error('Failed to fetch progress:', err);
            }
        };

        if (loading) {
            // Start polling immediately
            pollProgress();
            // Then set up interval
            progressInterval.current = setInterval(pollProgress, 100);
        }

        return () => {
            if (progressInterval.current) {
                clearInterval(progressInterval.current);
                progressInterval.current = null;
            }
        };
    }, [loading, dispatch]);

    const handleSubmit = async (promptData) => {
        try {
            dispatch(setProgress({ progress: 0, message: 'Starting generation...' }));
            await dispatch(generateIcon(promptData));
        } catch (err) {
            console.error('Generation failed:', err);
        }
    };

    return (
        <div className="image-generation">
            <h1>Generate Icon</h1>
            
            <div className="generation-grid">
                <div className="form-column">
                    <PromptInput onSubmit={handleSubmit} />
                    
                    {loading && (
                        <div className="progress-container">
                            <div className="progress-bar">
                                <div 
                                    className="progress-fill"
                                    style={{ width: `${progress}%` }}
                                >
                                    <span className="progress-text">{progress}%</span>
                                </div>
                            </div>
                            <p className="progress-message">{progressMessage}</p>
                        </div>
                    )}
                    
                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}
                </div>
                
                <div className="image-column">
                    {generatedImage ? (
                        <img 
                            src={generatedImage} 
                            alt="Generated icon" 
                            className="generated-image"
                        />
                    ) : (
                        <div className="placeholder-image">
                            <div className="placeholder-content">
                                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" 
                                        stroke="#666" 
                                        strokeWidth="2" 
                                        strokeLinecap="round"
                                    />
                                </svg>
                                <p>Your generated icon will appear here</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ImageGeneration; 