"""Core host process for ai-choreography-studio.

The host owns the lifecycle: bootstrap -> plugin discovery -> registry ->
generation pipeline -> export. Everything else is a plugin.
"""

__version__ = "0.6.3"
__all__ = ["__version__"]