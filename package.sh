#!/bin/bash

# Create necessary directories
mkdir -p /home/ubuntu/backend/services

# Copy backend files to the correct locations
cp /home/ubuntu/backend/app.py /home/ubuntu/backend/
cp /home/ubuntu/backend/models.py /home/ubuntu/backend/
cp /home/ubuntu/backend/services/modulargrid_parser.py /home/ubuntu/backend/services/
cp /home/ubuntu/backend/services/patch_generator.py /home/ubuntu/backend/services/
cp /home/ubuntu/requirements.txt /home/ubuntu/backend/

# Create __init__.py files
touch /home/ubuntu/backend/__init__.py
touch /home/ubuntu/backend/services/__init__.py

# Create a startup script
cat > /home/ubuntu/start.sh << 'EOF'
#!/bin/bash
echo "Starting Eurorack Patch Generator..."
docker-compose up
EOF

chmod +x /home/ubuntu/start.sh

echo "Application packaged successfully. Run ./start.sh to start the application."
