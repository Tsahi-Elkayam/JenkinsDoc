"""Centralized logger for the JenkinsDoc plugin.

Use ``LOG.debug(...)`` / ``LOG.info(...)`` / ``LOG.error(...)`` instead of
``print(...)``. Level is controlled by the ``debug_mode`` setting via
:func:`configure`.
"""

import logging

LOG = logging.getLogger("JenkinsDoc")

if not LOG.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("JenkinsDoc: %(message)s"))
    LOG.addHandler(_handler)
    LOG.propagate = False

LOG.setLevel(logging.WARNING)


def configure(settings):
    """Adjust log level based on the plugin settings."""
    debug = bool(settings and settings.get("debug_mode", False))
    LOG.setLevel(logging.DEBUG if debug else logging.WARNING)
