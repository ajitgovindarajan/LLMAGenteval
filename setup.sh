# scripts/setup.sh
#!/bin/bash

# Setup script for Android World evaluation
echo "Setting up Android World LLM Agent Evaluation..."

# Create directory structure
mkdir -p src prompts results/logs results/metrics

# Clone android_world repository (if not already present)
if [ ! -d "android_world" ]; then
    echo "Cloning android_world repository..."
    git clone https://github.com/google-research/android_world.git
    cd android_world
    pip install -e .
    cd ..
fi

# Install requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Create example configuration
echo "Creating example configuration..."
cat > .env.example << EOF
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANDROID_WORLD_DATA_PATH=./android_world/data
EOF

echo "Setup complete! Copy .env.example to .env and add your API keys."
echo "Then run: python src/main.py --data_path /path/to/android_world/data --api_key YOUR_KEY"