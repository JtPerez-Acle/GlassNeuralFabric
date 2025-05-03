"""
Simple Visualization Server for GlassNeuralFabric

This script sets up a simple HTTP server that:
1. Receives weight updates from the NeuroCapture module
2. Stores them in memory
3. Provides a web interface to visualize the weight changes

Run this alongside your training script to see weight changes in real-time.
"""

import http.server
import socketserver
import json
import threading
import webbrowser
import os
import time
from collections import defaultdict
import datetime

# HTML template for the visualization page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GlassNeuralFabric Weight Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin-bottom: 30px;
        }
        .controls {
            margin: 20px 0;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 4px;
        }
        select, button {
            padding: 8px;
            margin-right: 10px;
        }
        .stats {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .stat-box {
            background-color: #e9f7fe;
            border-radius: 4px;
            padding: 15px;
            margin-right: 15px;
            margin-bottom: 15px;
            min-width: 200px;
        }
        .stat-box h3 {
            margin-top: 0;
            color: #0077cc;
        }
        .refresh-button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
        .refresh-button:hover {
            background-color: #45a049;
        }
        .snapshots {
            margin-top: 20px;
        }
        .snapshot {
            background-color: #fff3cd;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 4px solid #ffc107;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>GlassNeuralFabric Weight Visualization</h1>
        
        <div class="controls">
            <button id="refreshButton" class="refresh-button">Refresh Data</button>
            <select id="layerSelect">
                <option value="all">All Layers</option>
            </select>
            <label>
                <input type="checkbox" id="showValues" checked> Show Values
            </label>
            <label>
                <input type="checkbox" id="showDeltas" checked> Show Deltas
            </label>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Updates</h3>
                <div id="totalUpdates">0</div>
            </div>
            <div class="stat-box">
                <h3>Layers Monitored</h3>
                <div id="layersCount">0</div>
            </div>
            <div class="stat-box">
                <h3>Significant Changes</h3>
                <div id="significantChanges">0</div>
            </div>
            <div class="stat-box">
                <h3>Last Update</h3>
                <div id="lastUpdate">Never</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="weightChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="deltaChart"></canvas>
        </div>
        
        <div class="snapshots">
            <h2>Model Snapshots</h2>
            <div id="snapshotsList"></div>
        </div>
    </div>

    <script>
        // Chart configuration
        let weightChart = null;
        let deltaChart = null;
        let weightData = {};
        let deltaData = {};
        let snapshots = [];
        
        // Initialize charts
        function initCharts() {
            const weightCtx = document.getElementById('weightChart').getContext('2d');
            const deltaCtx = document.getElementById('deltaChart').getContext('2d');
            
            weightChart = new Chart(weightCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Weight Values Over Time'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Updates'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Weight Value'
                            }
                        }
                    }
                }
            });
            
            deltaChart = new Chart(deltaCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Weight Deltas Over Time'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Updates'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Delta'
                            }
                        }
                    }
                }
            });
        }
        
        // Fetch data from the server
        function fetchData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    weightData = data.weight_history;
                    deltaData = data.delta_history;
                    snapshots = data.snapshots;
                    
                    updateStats(data);
                    updateLayerSelect(Object.keys(weightData));
                    updateCharts();
                    updateSnapshots();
                })
                .catch(error => console.error('Error fetching data:', error));
        }
        
        // Update statistics display
        function updateStats(data) {
            let totalUpdates = 0;
            let significantChanges = 0;
            
            // Count total updates
            Object.values(weightData).forEach(values => {
                totalUpdates += values.length;
            });
            
            // Count significant changes (delta > 0.1)
            Object.values(deltaData).forEach(deltas => {
                significantChanges += deltas.filter(d => Math.abs(d) > 0.1).length;
            });
            
            document.getElementById('totalUpdates').textContent = totalUpdates;
            document.getElementById('layersCount').textContent = Object.keys(weightData).length;
            document.getElementById('significantChanges').textContent = significantChanges;
            
            // Format last update time
            const lastUpdate = data.last_update ? new Date(data.last_update).toLocaleTimeString() : 'Never';
            document.getElementById('lastUpdate').textContent = lastUpdate;
        }
        
        // Update layer selection dropdown
        function updateLayerSelect(layers) {
            const select = document.getElementById('layerSelect');
            const currentValue = select.value;
            
            // Clear existing options except "All Layers"
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Add layer options
            layers.forEach(layer => {
                const option = document.createElement('option');
                option.value = layer;
                option.textContent = layer;
                select.appendChild(option);
            });
            
            // Restore previous selection if possible
            if (layers.includes(currentValue)) {
                select.value = currentValue;
            }
        }
        
        // Update chart displays
        function updateCharts() {
            const selectedLayer = document.getElementById('layerSelect').value;
            const showValues = document.getElementById('showValues').checked;
            const showDeltas = document.getElementById('showDeltas').checked;
            
            // Prepare datasets for weight chart
            const weightDatasets = [];
            const deltaDatasets = [];
            
            // Generate a color for each layer
            const getColor = (index) => {
                const colors = [
                    'rgb(75, 192, 192)',
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 159, 64)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 205, 86)',
                    'rgb(201, 203, 207)'
                ];
                return colors[index % colors.length];
            };
            
            // Add datasets for selected layers
            let index = 0;
            for (const [layer, values] of Object.entries(weightData)) {
                if (selectedLayer === 'all' || selectedLayer === layer) {
                    const color = getColor(index);
                    
                    if (showValues) {
                        weightDatasets.push({
                            label: layer,
                            data: values,
                            borderColor: color,
                            backgroundColor: color + '20',
                            tension: 0.1
                        });
                    }
                    
                    if (showDeltas && deltaData[layer]) {
                        deltaDatasets.push({
                            label: layer,
                            data: deltaData[layer],
                            borderColor: color,
                            backgroundColor: color + '20',
                            tension: 0.1
                        });
                    }
                    
                    index++;
                }
            }
            
            // Create labels (x-axis)
            const maxLength = Math.max(...Object.values(weightData).map(arr => arr.length), 0);
            const labels = Array.from({length: maxLength}, (_, i) => i + 1);
            
            // Update weight chart
            weightChart.data.labels = labels;
            weightChart.data.datasets = weightDatasets;
            weightChart.update();
            
            // Update delta chart
            deltaChart.data.labels = labels;
            deltaChart.data.datasets = deltaDatasets;
            deltaChart.update();
            
            // Add snapshot annotations
            addSnapshotAnnotations();
        }
        
        // Add vertical lines for snapshots
        function addSnapshotAnnotations() {
            // Clear existing annotations
            weightChart.options.plugins.annotation = {
                annotations: {}
            };
            deltaChart.options.plugins.annotation = {
                annotations: {}
            };
            
            // Add new annotations for each snapshot
            snapshots.forEach((snapshot, index) => {
                const id = `snapshot-${index}`;
                const annotation = {
                    type: 'line',
                    mode: 'vertical',
                    scaleID: 'x',
                    value: snapshot.step,
                    borderColor: 'rgba(255, 0, 0, 0.5)',
                    borderWidth: 2,
                    label: {
                        content: snapshot.reason,
                        enabled: true,
                        position: 'top'
                    }
                };
                
                if (!weightChart.options.plugins.annotation.annotations) {
                    weightChart.options.plugins.annotation.annotations = {};
                }
                if (!deltaChart.options.plugins.annotation.annotations) {
                    deltaChart.options.plugins.annotation.annotations = {};
                }
                
                weightChart.options.plugins.annotation.annotations[id] = annotation;
                deltaChart.options.plugins.annotation.annotations[id] = annotation;
            });
            
            weightChart.update();
            deltaChart.update();
        }
        
        // Update snapshots list
        function updateSnapshots() {
            const snapshotsList = document.getElementById('snapshotsList');
            snapshotsList.innerHTML = '';
            
            if (snapshots.length === 0) {
                snapshotsList.innerHTML = '<p>No snapshots available</p>';
                return;
            }
            
            snapshots.forEach(snapshot => {
                const snapshotDiv = document.createElement('div');
                snapshotDiv.className = 'snapshot';
                snapshotDiv.innerHTML = `
                    <strong>${snapshot.reason}</strong>
                    <div>Time: ${snapshot.timestamp}</div>
                    <div>Step: ${snapshot.step}</div>
                `;
                snapshotsList.appendChild(snapshotDiv);
            });
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            initCharts();
            fetchData();
            
            // Set up event listeners
            document.getElementById('refreshButton').addEventListener('click', fetchData);
            document.getElementById('layerSelect').addEventListener('change', updateCharts);
            document.getElementById('showValues').addEventListener('change', updateCharts);
            document.getElementById('showDeltas').addEventListener('change', updateCharts);
            
            // Auto-refresh every 5 seconds
            setInterval(fetchData, 5000);
        });
    </script>
</body>
</html>
"""

class VisualizationServer:
    """Simple server for visualizing weight changes"""
    
    def __init__(self, port=8080):
        self.port = port
        self.weight_history = defaultdict(list)
        self.delta_history = defaultdict(list)
        self.snapshots = []
        self.last_update = None
    
    def start(self):
        """Start the server"""
        handler = self._create_request_handler()
        
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(f"Server started at http://localhost:{self.port}")
            print("Open this URL in your browser to see the visualization")
            
            # Open browser automatically
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{self.port}")).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Server stopped")
    
    def _create_request_handler(self):
        """Create a request handler class with access to server data"""
        server = self
        
        class RequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(HTML_TEMPLATE.encode())
                elif self.path == "/api/data":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    
                    data = {
                        "weight_history": server.weight_history,
                        "delta_history": server.delta_history,
                        "snapshots": server.snapshots,
                        "last_update": server.last_update
                    }
                    
                    self.wfile.write(json.dumps(data).encode())
                else:
                    self.send_error(404)
            
            def do_POST(self):
                if self.path == "/update_weight" or self.path == "/":
                    content_length = int(self.headers["Content-Length"])
                    post_data = self.rfile.read(content_length)
                    weight_updates = json.loads(post_data.decode("utf-8"))
                    
                    # Process weight updates
                    for update in weight_updates:
                        layer_id = update["id"]
                        server.weight_history[layer_id].append(update["value"])
                        server.delta_history[layer_id].append(update["delta"])
                    
                    # Update last update time
                    server.last_update = datetime.datetime.now().isoformat()
                    
                    # Send response
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    
                    response = {
                        "status": "success",
                        "message": f"Processed {len(weight_updates)} updates"
                    }
                    
                    self.wfile.write(json.dumps(response).encode())
                elif self.path == "/create_snapshot":
                    content_length = int(self.headers["Content-Length"])
                    post_data = self.rfile.read(content_length)
                    snapshot_data = json.loads(post_data.decode("utf-8"))
                    
                    # Create a snapshot
                    snapshot = {
                        "reason": snapshot_data.get("reason", "Unnamed snapshot"),
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "step": len(next(iter(server.weight_history.values()), [])),
                    }
                    
                    server.snapshots.append(snapshot)
                    
                    # Send response
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    
                    response = {
                        "status": "success",
                        "message": "Snapshot created"
                    }
                    
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_error(404)
        
        return RequestHandler

def main():
    """Start the visualization server"""
    print("Starting GlassNeuralFabric Visualization Server")
    print("This server will receive weight updates from your neural network")
    print("and display them in a web interface.")
    
    # Get port from command line or use default
    import argparse
    parser = argparse.ArgumentParser(description="Start a visualization server for GlassNeuralFabric")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")
    args = parser.parse_args()
    
    # Start server
    server = VisualizationServer(port=args.port)
    server.start()

if __name__ == "__main__":
    main()
