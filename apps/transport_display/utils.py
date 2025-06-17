#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Utility functions for journey display system
"""

import os


def get_api_key() -> str:
    """Get API key from environment or user input"""
    api_key = os.getenv("TRANSPORT_API_KEY")
    if not api_key:
        api_key = input("Enter your Transport NSW API key: ").strip()
        if not api_key:
            raise ValueError("API key is required")
    return api_key
