#!/bin/bash
# Install documentation build dependencies
sudo apt install -y doxygen graphviz python3-pip
pip3 install --break-system-packages sphinx furo myst-parser sphinx-copybutton sphinxcontrib-mermaid linkify-it-py breathe
