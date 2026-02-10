"""
Vulnerable VFS (Virtual File System) implementation
Simulates Apache Commons VFS CVE (path traversal via URL-encoded sequences)

The vulnerability is in the path normalization - it checks for '..' traversal
BEFORE URL-decoding, so %2E%2E (URL-encoded ..) bypasses the check.
"""

import os
import urllib.parse
from enum import Enum

class NameScope(Enum):
    CHILD = "child"
    DESCENDENT = "descendent"  
    DESCENDENT_OR_SELF = "descendent_or_self"


def normalize_path(path):
    """
    VULNERABLE: Normalize path separators
    This mimics the vulnerable UriParser.fixSeparators behavior.
    It replaces backslashes with forward slashes but does NOT decode 
    percent-encoded characters early enough.
    """
    # Replace backslashes (like the original)
    path = path.replace('\\', '/')
    
    # The vulnerability: We decode %2F to / here, but NOT %2E to .
    # This mirrors the Apache Commons VFS bug where %2E%2E wasn't decoded
    # before path validation
    path = path.replace('%2f', '/').replace('%2F', '/')
    
    return path


def validate_scope(base_path, resolved_path, scope):
    """
    VULNERABLE: Validate that resolved path is within the allowed scope.
    The check happens BEFORE full URL decoding, so %2E%2E bypasses it.
    """
    # Normalize for comparison  
    base_normalized = os.path.normpath(base_path)
    
    # VULNERABILITY: We check containment on the path that still has %2E%2E encoded
    # This is the core of the Apache Commons VFS vulnerability
    if scope == NameScope.DESCENDENT or scope == NameScope.DESCENDENT_OR_SELF:
        # Check if the path contains literal '..' - but %2E%2E won't match!
        if '..' in resolved_path:
            return False, "Path traversal detected"
    
    return True, None


def resolve_file(base_path, relative_path, scope=NameScope.DESCENDENT):
    """
    VULNERABLE: Resolve a file path relative to a base path.
    Mimics FileObject.resolveFile(String name, NameScope scope)
    
    The vulnerability:
    1. Path is normalized with fixSeparators (only partial URL decoding)
    2. Scope validation checks for '..' but %2E%2E is still encoded
    3. Finally the path is URL-decoded, allowing traversal
    """
    # Step 1: Normalize path separators (VULNERABLE - partial decode)
    normalized_path = normalize_path(relative_path)
    
    # Step 2: Validate scope (VULNERABLE - checks before full decode)
    valid, error = validate_scope(base_path, normalized_path, scope)
    if not valid:
        raise ValueError(f"Path validation failed: {error}")
    
    # Step 3: NOW we URL-decode the path (too late - validation already passed)
    # This decodes %2E to . after validation
    decoded_path = urllib.parse.unquote(normalized_path)
    
    # Step 4: Build the full path
    full_path = os.path.normpath(os.path.join(base_path, decoded_path))
    
    # Final safety check that should have been done earlier (but wasn't in vulnerable version)
    # We intentionally skip this to simulate the vulnerable behavior
    # In the fixed version, this check would happen BEFORE step 3
    
    return full_path


def read_file(base_path, relative_path, scope=NameScope.DESCENDENT):
    """
    Read a file using the vulnerable VFS resolution.
    """
    try:
        resolved_path = resolve_file(base_path, relative_path, scope)
        
        if not os.path.exists(resolved_path):
            return None, f"File not found: {relative_path}"
        
        if os.path.isdir(resolved_path):
            # List directory contents
            files = os.listdir(resolved_path)
            return files, None
        
        with open(resolved_path, 'r') as f:
            return f.read(), None
            
    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"Error reading file: {str(e)}"
