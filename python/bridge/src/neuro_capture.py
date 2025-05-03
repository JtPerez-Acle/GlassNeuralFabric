"""
NeuroCapture module for capturing neural network state during training.

This module follows the modular architecture principles with clear interfaces
and single responsibility. It is developed using Test Driven Development.
"""

import torch
import time
import uuid
import queue
import threading
import requests
import logging
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class CaptureConfig:
    """Configuration for neural network state capture."""

    # Threshold for significant weight changes
    sig_level: float = 0.1

    # Interval for batching updates (seconds)
    batch_interval: float = 0.5

    # SpacetimeDB endpoint for weight updates
    endpoint: str = "http://localhost:3000/reducer/update_weight"

    # SpacetimeDB endpoint for creating snapshots
    snapshot_endpoint: str = "http://localhost:3000/reducer/create_snapshot"

    # Whether to capture gradients
    capture_gradients: bool = True

    # Whether to capture activations
    capture_activations: bool = False

    # Layer patterns to include (None means all)
    include_layers: Optional[List[str]] = None

    # Layer patterns to exclude
    exclude_layers: Optional[List[str]] = None


@dataclass
class CapturedWeight:
    """Captured weight data."""

    # Weight identifier (e.g., "layer1.weight")
    id: str

    # Current value of the weight
    value: float

    # Change in value since last update
    delta: float

    # Timestamp of the capture (nanoseconds)
    timestamp: int

    # Identifier for the sample that triggered this update
    origin_sample: str

    # Optional identifier for the agent
    agent_id: Optional[str] = None


class NeuroCapture:
    """
    Neural network state capture module.

    This class is responsible for capturing weight changes, gradients, and
    activations during neural network training.
    """

    def __init__(self, config: Optional[CaptureConfig] = None):
        """
        Initialize the neural network state capture module.

        Args:
            config: Configuration for capture behavior
        """
        self.config = config or CaptureConfig()
        self.model = None
        self.hook_handles = []
        self.q = queue.SimpleQueue()
        self.running = False
        self.thread = None
        self.logger = logging.getLogger("NeuroCapture")

    def attach_to_model(self, model: torch.nn.Module) -> None:
        """
        Attach capture hooks to a PyTorch model.

        Args:
            model: PyTorch model to attach to
        """
        self.logger.info(f"Attaching to model with {sum(p.numel() for p in model.parameters())} parameters")
        self.model = model
        self._install_hooks()
        self.running = True
        self.thread = threading.Thread(target=self._drain_queue, daemon=True)
        self.thread.start()

    def detach_from_model(self) -> None:
        """Remove capture hooks from the model."""
        if self.model:
            self.logger.info("Detaching from model")
            # Remove hooks
            for handle in self.hook_handles:
                handle.remove()
            self.hook_handles = []
            self.running = False
            if self.thread:
                self.thread.join(timeout=2.0)
            self.model = None

    def set_capture_config(self, config: CaptureConfig) -> None:
        """
        Configure what data to capture and at what frequency.

        Args:
            config: New configuration
        """
        self.logger.info(f"Updating capture configuration: sig_level={config.sig_level}, batch_interval={config.batch_interval}")
        self.config = config

    def get_captured_data(self) -> List[CapturedWeight]:
        """
        Get the currently captured data.

        Returns:
            List of captured weights
        """
        # This would typically return data from a buffer or cache
        # For simplicity, we'll return an empty list
        return []

    def _should_capture_layer(self, name: str) -> bool:
        """
        Determine if a layer should be captured based on include/exclude patterns.

        Args:
            name: Layer name

        Returns:
            True if the layer should be captured, False otherwise
        """
        # If include_layers is specified, only capture those layers
        if self.config.include_layers:
            return any(pattern in name for pattern in self.config.include_layers)

        # If exclude_layers is specified, exclude those layers
        if self.config.exclude_layers:
            return not any(pattern in name for pattern in self.config.exclude_layers)

        # Otherwise, capture all layers
        return True

    def _install_hooks(self) -> None:
        """Install hooks on model parameters."""
        for name, param in self.model.named_parameters():
            if not self._should_capture_layer(name):
                continue

            handle = param.register_hook(
                lambda grad, n=name, p=param: self._capture_gradient(n, p, grad)
            )
            self.hook_handles.append(handle)

            self.logger.debug(f"Installed hook for {name}")

    def _capture_gradient(self, name: str, param: torch.nn.Parameter, grad: torch.Tensor) -> None:
        """
        Capture gradient information during backpropagation.

        Args:
            name: Parameter name
            param: Parameter tensor
            grad: Gradient tensor
        """
        # Skip if gradients are not being captured
        if not self.config.capture_gradients:
            return

        # Calculate weight value and delta
        new_val = param.data.cpu().float().mean().item()
        old_val = new_val - grad.mean().item()

        # Only capture significant changes
        if abs(new_val - old_val) < self.config.sig_level:
            return

        # Create captured weight
        captured = CapturedWeight(
            id=name,
            value=new_val,
            delta=new_val - old_val,
            timestamp=time.time_ns(),
            origin_sample=str(uuid.uuid4()),
            agent_id=None
        )

        # Enqueue the captured data
        self.q.put(captured)

    def _drain_queue(self) -> None:
        """Drain the queue and send data to the endpoint."""
        while self.running:
            try:
                # Wait for a short time to batch updates
                time.sleep(self.config.batch_interval)

                # Collect all available updates
                batch = []
                while not self.q.empty():
                    batch.append(self.q.get())

                # Send the batch if not empty
                if batch:
                    self._send_batch(batch)
            except Exception as e:
                self.logger.error(f"Error in drain queue: {e}")

    def _send_batch(self, batch: List[Union[CapturedWeight, Dict[str, Any]]]) -> bool:
        """
        Send a batch of captured data to the SpacetimeDB endpoint.

        Args:
            batch: List of captured weights or dictionary data

        Returns:
            True if the batch was sent successfully, False otherwise
        """
        try:
            # Convert to dictionaries for JSON serialization if needed
            if batch and isinstance(batch[0], CapturedWeight):
                data = [
                    {
                        "id": item.id,
                        "value": item.value,
                        "delta": item.delta,
                        "timestamp": item.timestamp,
                        "origin_sample": item.origin_sample,
                        "agent_id": item.agent_id,
                    }
                    for item in batch
                ]
            else:
                # Already in dictionary format
                data = batch

            # Send to the SpacetimeDB endpoint
            self.logger.info(f"Sending batch to SpacetimeDB: {len(data)} items")
            response = requests.post(
                self.config.endpoint,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=2.0
            )

            if response.status_code != 200:
                self.logger.warning(f"Failed to send batch: {response.status_code} {response.text}")
                return False

            self.logger.debug(f"SpacetimeDB response: {response.text}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending batch to SpacetimeDB: {e}")
            return False


    def create_snapshot(self, reason: str, affected_weights: Optional[List[str]] = None) -> bool:
        """
        Create a snapshot of the model in SpacetimeDB.

        Args:
            reason: Reason for creating the snapshot
            affected_weights: List of weight IDs affected by this snapshot
                              (if None, all weights are considered affected)

        Returns:
            True if the snapshot was created successfully, False otherwise
        """
        try:
            # If no affected weights are specified, use all known weights
            if affected_weights is None:
                # This is a simplification - in a real implementation, we would
                # track all the weights we've seen and use those
                affected_weights = []

            # Create snapshot data
            snapshot_data = {
                "reason": reason,
                "affected_weights": affected_weights,
            }

            # Send to the SpacetimeDB endpoint
            self.logger.info(f"Creating model snapshot: {reason}")
            return self._send_batch(snapshot_data)
        except Exception as e:
            self.logger.error(f"Error creating snapshot: {e}")
            return False


# Convenience function to create and attach a capture module
def attach_capture(model: torch.nn.Module, config: Optional[CaptureConfig] = None) -> NeuroCapture:
    """
    Create and attach a capture module to a model.

    Args:
        model: PyTorch model to attach to
        config: Optional capture configuration

    Returns:
        The attached capture module
    """
    capture = NeuroCapture(config)
    capture.attach_to_model(model)
    return capture
