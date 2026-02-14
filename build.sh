#!/bin/bash
set -e
echo "Installing dependencies with prebuilt wheels only..."
pip install --only-binary :all: -r requirements.txt 2>&1 || pip install --prefer-binary -r requirements.txt
echo "Dependencies installed successfully!"
