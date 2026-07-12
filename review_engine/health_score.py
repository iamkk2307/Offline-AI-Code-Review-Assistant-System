"""
Health Score Calculator
========================
Implements the weighted Code Health Score formula.

Formula:
    Overall = (Quality × 0.30) + (Security × 0.25) + (Maintainability × 0.20) +
              (Performance × 0.15) + (Readability × 0.10)
"""


class HealthScoreCalculator:
    """Calculates the overall Code Health Score using configurable weights."""
    
    DEFAULT_WEIGHTS = {
        'quality':         0.30,
        'security':        0.25,
        'maintainability': 0.20,
        'performance':     0.15,
        'readability':     0.10,
    }
    
    def __init__(self, config=None):
        if config:
            self.weights = {
                'quality':         getattr(config, 'WEIGHT_QUALITY',         0.30),
                'security':        getattr(config, 'WEIGHT_SECURITY',        0.25),
                'maintainability': getattr(config, 'WEIGHT_MAINTAINABILITY', 0.20),
                'performance':     getattr(config, 'WEIGHT_PERFORMANCE',     0.15),
                'readability':     getattr(config, 'WEIGHT_READABILITY',     0.10),
            }
        else:
            self.weights = self.DEFAULT_WEIGHTS.copy()
    
    def calculate(self, quality_score: float, security_score: float,
                  maintainability_score: float, performance_score: float,
                  readability_score: float) -> float:
        """
        Calculate the overall Code Health Score.
        
        All input scores are expected to be in range [0, 100].
        Returns a float in range [0, 100].
        """
        score = (
            quality_score         * self.weights['quality'] +
            security_score        * self.weights['security'] +
            maintainability_score * self.weights['maintainability'] +
            performance_score     * self.weights['performance'] +
            readability_score     * self.weights['readability']
        )
        return round(max(0.0, min(100.0, score)), 1)
    
    @staticmethod
    def score_to_grade(score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90: return 'A+'
        if score >= 80: return 'A'
        if score >= 70: return 'B'
        if score >= 60: return 'C'
        if score >= 50: return 'D'
        return 'F'
    
    @staticmethod
    def score_to_label(score: float) -> str:
        """Convert numeric score to descriptive label."""
        if score >= 85: return 'Excellent'
        if score >= 70: return 'Good'
        if score >= 55: return 'Fair'
        if score >= 40: return 'Poor'
        return 'Critical'
    
    @staticmethod
    def score_to_color(score: float) -> str:
        """Convert numeric score to CSS color class."""
        if score >= 85: return 'excellent'
        if score >= 70: return 'good'
        if score >= 55: return 'fair'
        return 'poor'
