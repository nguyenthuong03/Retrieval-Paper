#!/bin/bash

# Update system
sudo yum update -y

# Install Python 3.9 and development tools
sudo yum install -y python3.9 python3.9-devel python3.9-pip gcc

# Install system dependencies
sudo yum install -y git

# Create app directory
mkdir -p ~/papermind
cd ~/papermind

# Clone the repository (replace with your repository URL)
git clone https://github.com/yourusername/papermind.git .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads vector_db

# Create systemd service file
sudo tee /etc/systemd/system/papermind.service << EOF
[Unit]
Description=PaperMind Flask Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/papermind
Environment="PATH=/home/ec2-user/papermind/venv/bin"
ExecStart=/home/ec2-user/papermind/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable papermind
sudo systemctl start papermind

# Configure Nginx
sudo yum install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/conf.d/papermind.conf << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /uploads {
        alias /home/ec2-user/papermind/uploads;
    }
}
EOF

# Start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Configure firewall
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

echo "Setup completed! The application should be running at http://your-ec2-public-ip" 