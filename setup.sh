#!/bin/bash

# ============================================================
# E-Commerce Sales & Customer Behavior Analysis
# Setup Script for macOS / Linux
# ============================================================

set -e  # Exit on any error

VENV_DIR="venv"
PYTHON_MIN="3.11"

echo ""
echo "============================================================"
echo "  E-Commerce Sales & Customer Behavior Analysis"
echo "  Environment Setup"
echo "============================================================"
echo ""

# --- Check Python version ---
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[INFO]  Python version detected: $PYTHON_VERSION"

# --- Create virtual environment ---
if [ -d "$VENV_DIR" ]; then
    echo "[INFO]  Virtual environment '$VENV_DIR' already exists. Skipping creation."
else
    echo "[INFO]  Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "[OK]    Virtual environment created at ./$VENV_DIR"
fi

# --- Activate virtual environment ---
echo "[INFO]  Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "[OK]    Virtual environment activated."

# --- Upgrade pip ---
echo "[INFO]  Upgrading pip..."
pip install --upgrade pip --quiet
echo "[OK]    pip upgraded."

# --- Install requirements ---
echo "[INFO]  Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "[OK]    All dependencies installed successfully."

# --- Register Jupyter kernel ---
echo "[INFO]  Registering Jupyter kernel..."
python -m ipykernel install --user --name ecommerce-analysis --display-name "Python (ecommerce-analysis)"
echo "[OK]    Jupyter kernel registered as 'ecommerce-analysis'."

echo ""
echo "============================================================"
echo "  Setup complete!"
echo ""
echo "  To activate the environment in future sessions:"
echo "    source venv/bin/activate"
echo ""
echo "  To launch Jupyter Notebook:"
echo "    jupyter notebook"
echo ""
echo "  To launch Jupyter Lab:"
echo "    jupyter lab"
echo "============================================================"
echo ""
