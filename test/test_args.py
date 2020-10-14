#!/usr/bin/env python3
"""Tests for anmad.args module."""

from anmad.common.args import parse_anmad_args

if __name__ == '__main__':
    ARGS = parse_anmad_args()
    print(ARGS)
