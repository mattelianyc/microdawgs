import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ImageGeneration from './pages/ImageGeneration';
import ModelTraining from './pages/ModelTraining';
import Navigation from './components/Navigation';
import './styles/global.scss';

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ImageGeneration />} />
            <Route path="/train" element={<ModelTraining />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 