import numpy as np
from typing import List, Dict, Union, Optional
import logging

logger = logging.getLogger(__name__)

class WeightProcessor:
    @staticmethod
    def normalize_weights(
        weights: Union[List[float], np.ndarray],
        min_val: float = 0.0,
        max_val: float = 1.0
    ) -> np.ndarray:
        """Normalize weights to specified range"""
        weights = np.array(weights)
        if weights.size == 0:
            return weights
            
        weights_min = weights.min()
        weights_max = weights.max()
        
        if weights_max == weights_min:
            return np.full_like(weights, (max_val + min_val) / 2)
            
        normalized = (weights - weights_min) / (weights_max - weights_min)
        return normalized * (max_val - min_val) + min_val

    @staticmethod
    def blend_weights(
        weights_a: np.ndarray,
        weights_b: np.ndarray,
        blend_factor: float = 0.5
    ) -> np.ndarray:
        """Blend two sets of weights"""
        if blend_factor < 0 or blend_factor > 1:
            raise ValueError("Blend factor must be between 0 and 1")
            
        if weights_a.shape != weights_b.shape:
            raise ValueError("Weight arrays must have same shape")
            
        return (1 - blend_factor) * weights_a + blend_factor * weights_b

    @staticmethod
    def calculate_attention(
        query: np.ndarray,
        key: np.ndarray,
        temperature: float = 1.0
    ) -> np.ndarray:
        """Calculate attention weights between query and key"""
        # Compute similarity scores
        similarity = np.dot(query, key.T) / temperature
        
        # Apply softmax
        exp_sim = np.exp(similarity - similarity.max())
        attention = exp_sim / exp_sim.sum()
        
        return attention

    @staticmethod
    def interpolate_weights(
        start_weights: np.ndarray,
        end_weights: np.ndarray,
        steps: int
    ) -> List[np.ndarray]:
        """Generate interpolated weight sequences"""
        if steps < 2:
            return [start_weights]
            
        alphas = np.linspace(0, 1, steps)
        return [
            WeightProcessor.blend_weights(start_weights, end_weights, alpha)
            for alpha in alphas
        ] 