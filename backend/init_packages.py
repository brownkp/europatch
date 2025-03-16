import os

# Initialize services directory
os.makedirs('/home/ubuntu/backend/services', exist_ok=True)

# Create __init__.py files to make directories into packages
with open('/home/ubuntu/backend/__init__.py', 'w') as f:
    f.write('# Backend package')

with open('/home/ubuntu/backend/services/__init__.py', 'w') as f:
    f.write('# Services package')
