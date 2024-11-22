import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import InfluenceSlider from './components/InfluenceSlider';
import PromptInput from './components/PromptInput';

function App() {
  const [influence, setInfluence] = useState(0.5);
  
  const handleUpload = (file) => {
    console.log('File uploaded:', file);
  };

  const handlePromptSubmit = (promptData) => {
    console.log('Prompt submitted:', promptData);
  };

  return (
    <div className="App">
      <h1>Image Generation Frontend</h1>
      <ImageUpload onUpload={handleUpload} />
      <InfluenceSlider 
        value={influence} 
        onChange={setInfluence}
      />
      <PromptInput onSubmit={handlePromptSubmit} />
    </div>
  );
}

export default App; 