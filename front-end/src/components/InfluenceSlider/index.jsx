import React from 'react';
import './styles.css';

const InfluenceSlider = ({
    value,
    onChange,
    min = 0,
    max = 1,
    step = 0.1,
    label = "Style Strength"
}) => {
    const percentage = ((value - min) / (max - min)) * 100;

    return (
        <div className="influence-slider">
            <label>
                {label}: {value.toFixed(1)}
            </label>
            <div className="slider-container">
                <input
                    type="range"
                    min={min}
                    max={max}
                    step={step}
                    value={value}
                    onChange={(e) => onChange(parseFloat(e.target.value))}
                    className="slider"
                    style={{
                        background: `linear-gradient(to right, #2196f3 ${percentage}%, #ddd ${percentage}%)`
                    }}
                />
                <div className="slider-labels">
                    <span>Subtle</span>
                    <span>Strong</span>
                </div>
            </div>
        </div>
    );
};

export default InfluenceSlider; 