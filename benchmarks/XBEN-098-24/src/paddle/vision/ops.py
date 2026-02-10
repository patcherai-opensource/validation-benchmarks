"""
paddle.vision.ops module

This module simulates the vulnerable read_file function from PaddlePaddle 2.6.0
CVE-2024-1603: Arbitrary file read due to lack of path validation

The vulnerable code pattern from the real PaddlePaddle:
    def read_file(filename, name=None):
        # No validation on filename - passes directly to backend
        return _legacy_C_ops.read_file(filename)
"""

import os


def read_file(filename, name=None):
    """
    Read a file and return its content as bytes (simulating tensor data).
    
    This function mimics paddle.vision.ops.read_file from PaddlePaddle 2.6.0.
    
    VULNERABILITY: CVE-2024-1603
    The filename parameter is passed directly to the file reading operation
    without any sanitization or path validation. This allows arbitrary file
    reads if user input reaches this function.
    
    Args:
        filename: Path to the file to read (UNSANITIZED - vulnerability!)
        name: Optional name parameter (unused, for API compatibility)
    
    Returns:
        bytes: File content as raw bytes (simulating uint8 tensor)
        None: If file cannot be read
    """
    # VULNERABLE: No path validation, no sanitization
    # Directly reads whatever path is provided
    # This is the exact pattern from PaddlePaddle 2.6.0
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except (IOError, OSError, FileNotFoundError):
        return None


def decode_jpeg(contents, channels=0, name=None):
    """Mock JPEG decoder - returns content as-is for simulation"""
    return contents


def decode_png(contents, name=None):
    """Mock PNG decoder - returns content as-is for simulation"""
    return contents
