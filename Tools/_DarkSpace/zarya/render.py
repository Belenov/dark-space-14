#!/usr/bin/env python3
"""Preview PNG of the finished station (from the in-memory model): python3 Tools/_DarkSpace/zarya/render.py out.png [scale]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import build, lib
lib.tile_id("Space")
build.transplant(); build.rays(); build.hub(); build.ferma_and_gallery()
lib.preview(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8)
