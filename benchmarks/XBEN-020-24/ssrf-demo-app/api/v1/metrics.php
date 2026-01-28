<?php
header('Content-Type: text/plain');
echo "# HELP predictml_requests_total Total number of prediction requests\n";
echo "# TYPE predictml_requests_total counter\n";
echo "predictml_requests_total{model=\"image_classifier\"} " . rand(1000, 9999) . "\n";
echo "predictml_requests_total{model=\"text_sentiment\"} " . rand(500, 5000) . "\n";
echo "predictml_requests_total{model=\"object_detector\"} " . rand(100, 1000) . "\n";
echo "\n";
echo "# HELP predictml_latency_seconds Request latency in seconds\n";
echo "# TYPE predictml_latency_seconds histogram\n";
echo "predictml_latency_seconds_bucket{le=\"0.1\"} " . rand(100, 500) . "\n";
echo "predictml_latency_seconds_bucket{le=\"0.5\"} " . rand(500, 2000) . "\n";
echo "predictml_latency_seconds_bucket{le=\"1.0\"} " . rand(2000, 5000) . "\n";
?>
