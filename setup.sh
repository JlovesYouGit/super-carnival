#!/bin/bash

echo "Setting up Network Traffic Management System..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit .env with your configuration"
fi

echo "Setup complete!"
echo "Activate virtual environment with: source venv/bin/activate"
echo "Run the system with: python main.py"
