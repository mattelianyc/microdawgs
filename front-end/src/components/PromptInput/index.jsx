import React, { useState, useEffect } from 'react';
import './styles.css';

const PromptInput = ({ 
    onSubmit, 
    maxLength = 1000,
    placeholder = "Describe your image..."
}) => {
    const [prompt, setPrompt] = useState('');
    const [negativePrompt, setNegativePrompt] = useState('');
    const [error, setError] = useState(null);
    const [charCount, setCharCount] = useState(0);

    useEffect(() => {
        setCharCount(prompt.length);
    }, [prompt]);

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!prompt.trim()) {
            setError('Please enter a prompt');
            return;
        }

        if (prompt.length > maxLength) {
            setError(`Prompt too long. Maximum length is ${maxLength} characters`);
            return;
        }

        onSubmit({
            prompt: prompt.trim(),
            negative_prompt: negativePrompt.trim() || null
        });
        setError(null);
    };

    return (
        <form onSubmit={handleSubmit} className="prompt-form">
            <div className="input-group">
                <label htmlFor="prompt">Prompt</label>
                <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder={placeholder}
                    rows={4}
                />
                <span className="char-count">
                    {charCount}/{maxLength}
                </span>
            </div>

            <div className="input-group">
                <label htmlFor="negative-prompt">Negative Prompt (Optional)</label>
                <textarea
                    id="negative-prompt"
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    placeholder="What to avoid in the image..."
                    rows={2}
                />
            </div>

            {error && <p className="error-message">{error}</p>}
            
            <button type="submit" className="submit-button">
                Generate
            </button>
        </form>
    );
};

export default PromptInput; 