#!/usr/bin/env python3
"""Tests for anmad.logging module."""

import anmad.logging

if __name__ == '__main__':
    LOGGER = anmad.logging.logsetup()
    LOGGER.debug("anmad.logging test ok")
