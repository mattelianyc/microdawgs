// Image processing utilities
export const resizeImage = (file, maxWidth = 1024, maxHeight = 1024) => {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;

            if (width > height) {
                if (width > maxWidth) {
                    height = Math.round((height * maxWidth) / width);
                    width = maxWidth;
                }
            } else {
                if (height > maxHeight) {
                    width = Math.round((width * maxHeight) / height);
                    height = maxHeight;
                }
            }

            canvas.width = width;
            canvas.height = height;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob((blob) => {
                resolve(new File([blob], file.name, { type: file.type }));
            }, file.type);
        };
        img.src = URL.createObjectURL(file);
    });
};

// Validation utilities
export const validatePrompt = (prompt) => {
    if (!prompt || !prompt.trim()) {
        throw new Error('Prompt is required');
    }
    if (prompt.length > 1000) {
        throw new Error('Prompt is too long (max 1000 characters)');
    }
    return prompt.trim();
};

export const validateFile = (file) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

    if (!file) {
        throw new Error('File is required');
    }
    if (file.size > maxSize) {
        throw new Error('File is too large (max 10MB)');
    }
    if (!allowedTypes.includes(file.type)) {
        throw new Error('Invalid file type (JPEG, PNG, or WebP only)');
    }
    return true;
};

// Error handling utilities
export const formatError = (error) => {
    if (typeof error === 'string') {
        return error;
    }
    if (error.response && error.response.data) {
        return error.response.data.message || 'Server error';
    }
    return error.message || 'Unknown error';
}; 