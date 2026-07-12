"""
Base Report Generator
======================
Abstract base class for all report generators.
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime


class BaseReportGenerator(ABC):
    """Base class for report generators. Defines the generate() contract."""
    
    @property
    @abstractmethod
    def format(self) -> str:
        """Report format identifier (e.g., 'pdf', 'html')."""
        ...
    
    @property
    @abstractmethod
    def extension(self) -> str:
        """File extension for output (e.g., '.pdf', '.html')."""
        ...
    
    @abstractmethod
    def generate(self, analysis_data: dict, output_dir: str) -> str:
        """
        Generate report and save to output_dir.
        Returns the absolute path to the generated file.
        """
        ...
    
    def _make_output_path(self, output_dir: str, prefix: str = 'report') -> str:
        """Generate a timestamped output file path."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}{self.extension}"
        return os.path.join(output_dir, filename)
    
    def _get_score_label(self, score: float) -> str:
        if score >= 85: return 'Excellent'
        if score >= 70: return 'Good'
        if score >= 55: return 'Fair'
        if score >= 40: return 'Poor'
        return 'Critical'
