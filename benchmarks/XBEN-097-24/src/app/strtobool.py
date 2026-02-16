def strtobool(val):
    """Convert a string representation of truth to True or False."""
    if isinstance(val, bool):
        return val
    val = str(val).lower().strip()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"Invalid truth value {val!r}")
