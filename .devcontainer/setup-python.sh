#!/bin/bash
# This script sets up the Python environment for the AI Avatar project

echo "Setting up Python environment for AI Avatar..."

# Get the workspace folder name dynamically
WORKSPACE_NAME=$(basename "/workspaces/$(ls /workspaces/ | head -1)")
WORKSPACE_PATH="/workspaces/$WORKSPACE_NAME"

echo "📁 Working in: $WORKSPACE_PATH"

# Use conda environment if it exists
if command -v conda &> /dev/null; then
    echo "Using conda environment..."
    
    # Activate conda environment
    source $(conda info --base)/etc/profile.d/conda.sh
    
    # Use existing conda env or create a new one
    if conda info --envs | grep -q "aiavatar"; then
        conda activate aiavatar
        echo "Activated existing conda environment 'aiavatar'."
    else
        echo "Creating new conda environment 'aiavatar'..."
        conda create -n aiavatar python=3.11 -y
        conda activate aiavatar
        echo "New conda environment 'aiavatar' created and activated."
    fi
    
    # Install requirements
    if [ -f "$WORKSPACE_PATH/requirements.txt" ]; then
        echo "Installing packages from requirements.txt..."
        pip install -r "$WORKSPACE_PATH/requirements.txt"
    else
        echo "No requirements.txt found in project root."
    fi
    
    # Install development requirements
    if [ -f "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt" ]; then
        echo "Installing development requirements..."
        pip install -r "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt"
    else
        echo "No requirements-dev.txt found."
    fi
else
    echo "Conda not found, using system Python..."
    # Use virtualenv if preferred
    if command -v python -m venv &> /dev/null; then
        echo "Setting up virtual environment..."
        python -m venv .venv
        source .venv/bin/activate
        
        # Install requirements
        if [ -f "$WORKSPACE_PATH/requirements.txt" ]; then
            echo "Installing packages from requirements.txt..."
            pip install -r "$WORKSPACE_PATH/requirements.txt"
        else
            echo "No requirements.txt found in project root."
        fi
        
        # Install development requirements
        if [ -f "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt" ]; then
            echo "Installing development requirements..."
            pip install -r "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt"
        else
            echo "No requirements-dev.txt found."
        fi
    else
        # Fall back to system Python
        echo "Using system Python..."
        if [ -f "$WORKSPACE_PATH/requirements.txt" ]; then
            echo "Installing packages from requirements.txt..."
            pip install -r "$WORKSPACE_PATH/requirements.txt"
        else
            echo "No requirements.txt found in project root."
        fi
        
        # Install development requirements
        if [ -f "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt" ]; then
            echo "Installing development requirements..."
            pip install -r "$WORKSPACE_PATH/.devcontainer/requirements-dev.txt"
        else
            echo "No requirements-dev.txt found."
        fi
    fi
fi

echo "Python setup complete for AI Avatar!"
