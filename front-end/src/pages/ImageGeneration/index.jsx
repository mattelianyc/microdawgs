import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { generateIcon, clearState } from '../../slices/imageGenerationSlice';
import ImageGeneration from '../../components/ImageGeneration';

const ImageGenerationPage = () => {
    const dispatch = useDispatch();
    const { loading, error, generatedImage } = useSelector(state => state.imageGeneration);

    const handleGenerate = async (promptData) => {
        await dispatch(generateIcon(promptData));
    };

    const handleClear = () => {
        dispatch(clearState());
    };

    return (
        <div className="page-container">
            <ImageGeneration 
                onSubmit={handleGenerate}
                onClear={handleClear}
                loading={loading}
                error={error}
                generatedImage={generatedImage}
            />
        </div>
    );
};

export default ImageGenerationPage; 