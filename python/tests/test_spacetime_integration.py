"""
Tests for SpacetimeDB integration in the NeuroCapture module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import time
import threading

from bridge.src import NeuroCapture, CaptureConfig, attach_capture
from bridge.src.neuro_capture import CapturedWeight


class TestSpacetimeIntegration(unittest.TestCase):
    """Test the integration with SpacetimeDB."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CaptureConfig(
            sig_level=0.01,
            batch_interval=0.1,
            endpoint="http://localhost:3000/reducer/update_weight",
            capture_gradients=True,
            capture_activations=False,
        )
        self.capture = NeuroCapture(self.config)

    @patch('requests.post')
    def test_send_batch(self, mock_post):
        """Test sending a batch of weight updates to SpacetimeDB."""
        # Arrange
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}
        
        batch = [
            {
                "id": "layer1.w1",
                "value": 0.5,
                "delta": 0.1,
                "timestamp": int(time.time() * 1000),
                "origin_sample": "test_sample",
                "agent_id": None
            }
        ]
        
        # Act
        result = self.capture._send_batch(batch)
        
        # Assert
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            self.config.endpoint,
            json=batch,
            headers={"Content-Type": "application/json"}
        )

    @patch('requests.post')
    def test_send_batch_error(self, mock_post):
        """Test handling errors when sending a batch."""
        # Arrange
        mock_post.side_effect = Exception("Connection error")
        
        batch = [
            {
                "id": "layer1.w1",
                "value": 0.5,
                "delta": 0.1,
                "timestamp": int(time.time() * 1000),
                "origin_sample": "test_sample",
                "agent_id": None
            }
        ]
        
        # Act
        result = self.capture._send_batch(batch)
        
        # Assert
        self.assertFalse(result)

    @patch('bridge.src.neuro_capture.NeuroCapture._send_batch')
    def test_batch_processing_thread(self, mock_send_batch):
        """Test that the batch processing thread correctly sends batches."""
        # Arrange
        mock_send_batch.return_value = True
        self.capture.running = True
        self.capture.batch_queue = MagicMock()
        
        # Create a batch
        batch = [
            CapturedWeight(
                id="layer1.w1",
                value=0.5,
                delta=0.1,
                timestamp=int(time.time() * 1000),
                origin_sample="test_sample",
                agent_id=None
            )
        ]
        
        # Mock the queue to return our batch once, then raise Empty
        self.capture.batch_queue.get.side_effect = [batch, Exception("Empty")]
        
        # Act - run the batch processing thread for a short time
        thread = threading.Thread(target=self.capture._batch_processing_thread)
        thread.daemon = True
        thread.start()
        time.sleep(0.2)  # Give the thread time to process
        self.capture.running = False  # Stop the thread
        thread.join(timeout=0.5)
        
        # Assert
        mock_send_batch.assert_called_once()
        # Verify the batch was converted to the correct format
        sent_batch = mock_send_batch.call_args[0][0]
        self.assertEqual(len(sent_batch), 1)
        self.assertEqual(sent_batch[0]["id"], "layer1.w1")
        self.assertEqual(sent_batch[0]["value"], 0.5)
        self.assertEqual(sent_batch[0]["delta"], 0.1)

    @patch('bridge.src.neuro_capture.NeuroCapture._send_batch')
    def test_create_snapshot(self, mock_send_batch):
        """Test creating a model snapshot."""
        # Arrange
        mock_send_batch.return_value = True
        self.capture.config.snapshot_endpoint = "http://localhost:3000/reducer/create_snapshot"
        
        # Act
        result = self.capture.create_snapshot("Test snapshot", ["layer1.w1", "layer1.w2"])
        
        # Assert
        self.assertTrue(result)
        mock_send_batch.assert_called_once()
        # Verify the snapshot data was formatted correctly
        sent_data = mock_send_batch.call_args[0][0]
        self.assertEqual(sent_data["reason"], "Test snapshot")
        self.assertEqual(len(sent_data["affected_weights"]), 2)
        self.assertIn("layer1.w1", sent_data["affected_weights"])
        self.assertIn("layer1.w2", sent_data["affected_weights"])


if __name__ == '__main__':
    unittest.main()
