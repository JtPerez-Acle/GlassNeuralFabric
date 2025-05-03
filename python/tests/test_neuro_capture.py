"""
Tests for the NeuroCapture module.

These tests follow the Test Driven Development approach:
1. Write a failing test
2. Implement minimal code to make the test pass
3. Refactor while maintaining passing tests
"""

import pytest
import torch
import time
from unittest.mock import MagicMock, patch
import threading
import queue

from bridge.src.neuro_capture import NeuroCapture, CaptureConfig, CapturedWeight, attach_capture


class SimpleModel(torch.nn.Module):
    """Simple model for testing."""

    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(10, 5)
        self.fc2 = torch.nn.Linear(5, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


@pytest.fixture
def model():
    """Create a simple model for testing."""
    return SimpleModel()


@pytest.fixture
def capture_config():
    """Create a capture configuration for testing."""
    return CaptureConfig(
        sig_level=0.01,
        batch_interval=0.1,
        endpoint="http://localhost:5000/test",
        capture_gradients=True,
        capture_activations=False,
    )


def test_init():
    """Test initialization of NeuroCapture."""
    # Arrange & Act
    capture = NeuroCapture()

    # Assert
    assert capture.model is None
    assert capture.hook_handles == []
    assert capture.running is False
    assert capture.thread is None
    assert capture.config.sig_level == 0.1  # Default value
    assert capture.config.batch_interval == 0.5  # Default value


def test_init_with_config(capture_config):
    """Test initialization with custom config."""
    # Arrange & Act
    capture = NeuroCapture(capture_config)

    # Assert
    assert capture.config.sig_level == 0.01
    assert capture.config.batch_interval == 0.1
    assert capture.config.endpoint == "http://localhost:5000/test"


def test_attach_to_model(model):
    """Test attaching to a model."""
    # Arrange
    capture = NeuroCapture()

    # Act
    with patch.object(capture, '_install_hooks') as mock_install:
        capture.attach_to_model(model)

        # Assert
        assert capture.model is model
        assert capture.running is True
        assert capture.thread is not None
        mock_install.assert_called_once()


def test_detach_from_model(model):
    """Test detaching from a model."""
    # Arrange
    capture = NeuroCapture()
    mock_handle = MagicMock()
    capture.hook_handles = [mock_handle]
    capture.model = model
    capture.running = True
    capture.thread = MagicMock()

    # Act
    capture.detach_from_model()

    # Assert
    assert capture.model is None
    assert capture.hook_handles == []
    assert capture.running is False
    mock_handle.remove.assert_called_once()
    capture.thread.join.assert_called_once()


def test_set_capture_config(capture_config):
    """Test updating the capture configuration."""
    # Arrange
    capture = NeuroCapture()
    original_config = capture.config

    # Act
    capture.set_capture_config(capture_config)

    # Assert
    assert capture.config is capture_config
    assert capture.config is not original_config


def test_should_capture_layer():
    """Test layer filtering logic."""
    # Arrange
    capture = NeuroCapture()

    # Test with no filters (should capture all)
    assert capture._should_capture_layer("layer1.weight") is True

    # Test with include filter
    capture.config.include_layers = ["layer1"]
    assert capture._should_capture_layer("layer1.weight") is True
    assert capture._should_capture_layer("layer2.weight") is False

    # Test with exclude filter
    capture.config.include_layers = None
    capture.config.exclude_layers = ["layer1"]
    assert capture._should_capture_layer("layer1.weight") is False
    assert capture._should_capture_layer("layer2.weight") is True


def test_install_hooks(model):
    """Test hook installation."""
    # Arrange
    capture = NeuroCapture()
    capture.model = model

    # Act
    with patch.object(torch.nn.Parameter, 'register_hook') as mock_register:
        mock_register.return_value = MagicMock()
        capture._install_hooks()

        # Assert
        # Model has 2 layers with parameters
        assert mock_register.call_count > 0
        assert len(capture.hook_handles) > 0


def test_capture_gradient():
    """Test gradient capture logic."""
    # Arrange
    capture = NeuroCapture(CaptureConfig(sig_level=0.01))
    mock_param = MagicMock()
    mock_param.data.cpu().float().mean.return_value.item.return_value = 0.5
    mock_grad = MagicMock()
    mock_grad.mean.return_value.item.return_value = 0.1

    # Act
    with patch.object(capture, 'q') as mock_queue:
        capture._capture_gradient("layer1.weight", mock_param, mock_grad)

        # Assert
        mock_queue.put.assert_called_once()
        captured = mock_queue.put.call_args[0][0]
        assert captured.id == "layer1.weight"
        assert captured.value == 0.5
        assert abs(captured.delta - 0.1) < 1e-10  # new_val - old_val, where old_val = new_val - grad.mean().item()
        assert captured.timestamp > 0
        assert captured.origin_sample is not None


def test_capture_gradient_below_threshold():
    """Test that gradients below threshold are not captured."""
    # Arrange
    capture = NeuroCapture(CaptureConfig(sig_level=0.5))
    mock_param = MagicMock()
    mock_param.data.cpu().float().mean.return_value.item.return_value = 0.5
    mock_grad = MagicMock()
    mock_grad.mean.return_value.item.return_value = 0.1

    # Act
    with patch.object(capture, 'q') as mock_queue:
        capture._capture_gradient("layer1.weight", mock_param, mock_grad)

        # Assert - delta is 0.1, below threshold of 0.5
        mock_queue.put.assert_not_called()


def test_drain_queue():
    """Test queue draining logic."""
    # Arrange
    capture = NeuroCapture(CaptureConfig(batch_interval=0.01))
    capture.running = True
    capture.q = queue.SimpleQueue()

    # Add some items to the queue
    weight1 = CapturedWeight(
        id="layer1.weight",
        value=0.5,
        delta=0.1,
        timestamp=time.time_ns(),
        origin_sample="test1",
    )
    weight2 = CapturedWeight(
        id="layer2.weight",
        value=0.3,
        delta=0.2,
        timestamp=time.time_ns(),
        origin_sample="test2",
    )
    capture.q.put(weight1)
    capture.q.put(weight2)

    # Act
    with patch.object(capture, '_send_batch') as mock_send:
        # Run the drain method in a thread
        thread = threading.Thread(target=capture._drain_queue)
        thread.daemon = True
        thread.start()

        # Wait a bit for the thread to process
        time.sleep(0.05)

        # Stop the thread
        capture.running = False
        thread.join(timeout=0.1)

        # Assert
        mock_send.assert_called_once()
        batch = mock_send.call_args[0][0]
        assert len(batch) == 2
        assert batch[0].id == "layer1.weight"
        assert batch[1].id == "layer2.weight"


def test_send_batch():
    """Test batch sending logic."""
    # Arrange
    capture = NeuroCapture()
    batch = [
        CapturedWeight(
            id="layer1.weight",
            value=0.5,
            delta=0.1,
            timestamp=time.time_ns(),
            origin_sample="test1",
        ),
        CapturedWeight(
            id="layer2.weight",
            value=0.3,
            delta=0.2,
            timestamp=time.time_ns(),
            origin_sample="test2",
        ),
    ]

    # Act
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        capture._send_batch(batch)

        # Assert
        mock_post.assert_called_once()
        json_data = mock_post.call_args[1]['json']
        assert len(json_data) == 2
        assert json_data[0]['id'] == "layer1.weight"
        assert json_data[0]['value'] == 0.5
        assert json_data[0]['delta'] == 0.1
        assert json_data[1]['id'] == "layer2.weight"


def test_send_batch_error_handling():
    """Test error handling in batch sending."""
    # Arrange
    capture = NeuroCapture()
    batch = [
        CapturedWeight(
            id="layer1.weight",
            value=0.5,
            delta=0.1,
            timestamp=time.time_ns(),
            origin_sample="test1",
        ),
    ]

    # Act & Assert - should not raise exception
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("Test error")
        capture._send_batch(batch)  # Should handle the exception


def test_attach_capture_convenience_function(model):
    """Test the convenience function for attaching capture."""
    # Arrange & Act
    with patch.object(NeuroCapture, 'attach_to_model') as mock_attach:
        capture = attach_capture(model)

        # Assert
        assert isinstance(capture, NeuroCapture)
        mock_attach.assert_called_once_with(model)


def test_integration_with_real_model():
    """Integration test with a real PyTorch model."""
    # Arrange
    model = SimpleModel()
    capture = NeuroCapture(CaptureConfig(sig_level=0.0))  # Capture all changes

    # Act
    with patch.object(capture, 'q') as mock_queue:
        capture.attach_to_model(model)

        # Create a simple input and target
        x = torch.randn(1, 10)
        target = torch.randn(1, 2)

        # Forward and backward pass
        output = model(x)
        loss = torch.nn.functional.mse_loss(output, target)
        loss.backward()

        # Assert
        assert mock_queue.put.call_count > 0  # Some weights should be captured
