from typing import List, Tuple, Dict
import numpy as np
from sklearn.linear_model import Lasso



class PaintMixPredictor:
    def __init__(self, target_rgb: List[int]):
        self.target_rgb = target_rgb
        self.base_colors = {
            "titanium_white": [255, 255, 255],
            "carbon_black": [10, 10, 10],
            "cadmium_yellow": [255, 200, 0],
            "ultramarine_blue": [50, 80, 200],
            "quinacridone_magenta": [180, 70, 154],
            "phthalo_blue": [0, 15, 137],
            "yellow_ochre": [204, 119, 34],
            "burnt_sienna": [233, 116, 81]
        }
        
        self.wavelengths = np.linspace(400, 700, 30)

    def normalize_rgb(self, rgb: List[int]) -> List[float]:
        return [x / 255.0 for x in rgb]


    def estimate_reflectance(self, rgb: List[int]) -> np.ndarray:
        """Estimate reflectance spectrum using Gaussian peaks for RGB channels."""
        normalized_rgb = self.normalize_rgb(rgb)
        peak_wavelengths = [650, 530, 450]  # Red, Green, Blue peaks
        sigma = 50  # Spread of Gaussian

        reflectance = np.zeros_like(self.wavelengths)
        for i, peak in enumerate(peak_wavelengths):
            reflectance += normalized_rgb[i] * np.exp(-((self.wavelengths - peak) ** 2) / (2 * sigma**2))

        return reflectance
    
    def generate_base_color_reflectances(self) -> Dict[str, np.ndarray]:
        """Generate estimated reflectance spectra for all base colors."""
        return {name: self.estimate_reflectance(rgb) for name, rgb in self.base_colors.items()}
    
    def reflectance_to_KS(self, R: np.ndarray) -> np.array:
        return (1-R)**2 / (2*R)
    
    def calculate_mixture(self) -> Dict[str,float]:

        base_reflectances = self.generate_base_color_reflectances()
        base_KS = {name: self.reflectance_to_KS(R) for name, R in base_reflectances.items()}

        target_reflectance = self.estimate_reflectance(self.target_rgb)
        target_KS = self.reflectance_to_KS(target_reflectance)

        normalized_rgb = self.normalize_rgb(self.target_rgb)
        brightness = sum(normalized_rgb) / 3.0

        A = np.array(list(base_KS.values())).T  # Each column is a base pigment
        b = target_KS

        # Calculate alpha (regularization strength) based on target color properties
        # This helps adjust the sparsity level adaptively
        # Lower alpha for dark colors that need more precision
        base_alpha = 0.01
        if brightness < 0.3:
            alpha = base_alpha * 0.5
        elif brightness > 0.7:
            alpha = base_alpha * 2.0
        else:
            alpha = base_alpha
            
        # Solve using Lasso regression with non-negative constraint
        lasso = Lasso(alpha=alpha, positive=True, max_iter=10000, fit_intercept=False)
        lasso.fit(A, b)
        pigment_weights = lasso.coef_

        # Normalize weights to get percentages
        total_weight = np.sum(pigment_weights)
        if total_weight > 0:
            pigment_weights /= total_weight

        # Map back to pigment names
        pigment_names = list(base_KS.keys())
        return {name: weight for name, weight in zip(pigment_names, pigment_weights)}





# Example usage
# predictor = PaintMixPredictor([0, 128, 128])  # Target color: Quinacridone Magenta
# mixture = predictor.calculate_mixture()

# print(mixture)