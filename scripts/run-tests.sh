#!/bin/bash

# Go to project directory
cd "$(dirname "$0")/.."

pytest-3 --cov=sjb --cov-report=html tests/
