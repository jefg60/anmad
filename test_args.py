#!/usr/bin/env python3
"""Tests for anmad.args module."""

import anmad.args

if __name__ == '__main__':
    ARGS = anmad.args.parse_args()
    print(ARGS)
