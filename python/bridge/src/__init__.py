"""
NeuroSpacetime bridge module.

This module provides functionality for capturing neural network state during training.
"""

from .neuro_capture import NeuroCapture, CaptureConfig, CapturedWeight, attach_capture

__all__ = ['NeuroCapture', 'CaptureConfig', 'CapturedWeight', 'attach_capture']
