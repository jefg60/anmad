#!/usr/bin/env python3
"""Tests for anmad.logging module."""

import anmad.logging
import anmad.args

if __name__ == '__main__':
    ARGS = anmad.args.parse_args()
    LOGGER = anmad.logging.logsetup(ARGS)
    LOGGER.debug("anmad.logging test ok")
