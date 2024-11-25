import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ImageUpload from '../../components/ImageUpload';
import InfluenceSlider from '../../components/InfluenceSlider';
import PromptInput from '../../components/PromptInput';
import { generateIcon, clearGeneratedImage } from '../../slices/imageGenerationSlice';
import './styles.scss';

const ImageGeneration = () => {
  const dispatch = useDispatch();
  const { loading, error, generatedImage } = useSelector((state) => state.imageGeneration);
  const [styleStrength, setStyleStrength] = useState(0.5);

  const handlePromptSubmit = async (promptData) => {
    dispatch(generateIcon({
      prompt: promptData.prompt,
      num_steps: 20,
      guidance_scale: 7.5,
      ...(promptData.negative_prompt && { negative_prompt: promptData.negative_prompt })
    }));
  };

  return (
    <div className="image-generation-page">
      <h1>Generate Icons</h1>
      <ImageUpload />
      <InfluenceSlider 
        value={styleStrength}
        onChange={setStyleStrength}
        label="Style Strength"
      />
      <PromptInput onSubmit={handlePromptSubmit} />
      
      {loading && <div className="loading">Generating...</div>}
      {error && <div className="error">{error}</div>}
      {generatedImage && (
        <div className="result">
          <img src={generatedImage} alt="Generated icon" />
          <button 
            onClick={() => dispatch(clearGeneratedImage())}
            className="clear-button"
          >
            Clear Image
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageGeneration; 