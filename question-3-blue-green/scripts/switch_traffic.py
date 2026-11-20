#!/usr/bin/env python3
"""
Nginx / Reverse Proxy Upstream Switch Script
Module: question-3-blue-green/scripts/switch_traffic.py
Description: Switches the active upstream in Nginx between Blue and Green configuration.
"""

import sys
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCKER_DIR = os.path.join(BASE_DIR, "docker")

def switch_target(color):
    color = color.lower()
    if color not in ["blue", "green"]:
        print(f"Error: Target must be 'blue' or 'green'. Received '{color}'")
        sys.exit(1)

    source_file = os.path.join(DOCKER_DIR, f"nginx-{color}.conf")
    target_file = os.path.join(DOCKER_DIR, "upstream.conf")

    if not os.path.exists(source_file):
        print(f"Error: Source configuration {source_file} not found.")
        sys.exit(1)

    shutil.copy2(source_file, target_file)
    print(f"[SWITCH SUCCESS] Active upstream switched to: {color.upper()}")
    print("If running with Docker Nginx container, reload with: docker exec nginx-reverse-proxy nginx -s reload")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python switch_traffic.py [blue|green]")
        sys.exit(1)
    switch_target(sys.argv[1])
