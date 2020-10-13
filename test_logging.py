#!/usr/bin/env python3
"""Tests for anmad.logging module."""

from anmad.common.logging import logsetup
from anmad.common.args import parse_anmad_args

if __name__ == '__main__':
    ARGS = parse_anmad_args()
    LOGGER = logsetup(ARGS, __file__)
    LOGGER.debug("anmad.logging test ok")
