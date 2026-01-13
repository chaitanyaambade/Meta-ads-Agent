"""
Utility functions for META Marketing Agent System
"""

# Global quiet mode flag
QUIET_MODE = False


def set_quiet_mode(quiet: bool):
    """Set quiet mode globally"""
    global QUIET_MODE
    QUIET_MODE = quiet


def is_quiet_mode() -> bool:
    """Check if quiet mode is enabled"""
    return QUIET_MODE


def log_debug(msg: str):
    """Print debug message only if not in quiet mode"""
    if not QUIET_MODE:
        print(msg)


def log_info(msg: str):
    """Print info message (always shown)"""
    print(msg)


def log_section(title: str):
    """Print section header"""
    if not QUIET_MODE:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
