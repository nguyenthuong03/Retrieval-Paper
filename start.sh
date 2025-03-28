#!/bin/bash

# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
mkdir -p ~/papermind
cd ~/papermind

# Pull the latest image
docker pull yourusername/papermind:latest

# Run the container
docker run -d \
  -p 80:5000 \
  -v ~/papermind/uploads:/app/uploads \
  -v ~/papermind/vector_db:/app/vector_db \
  --restart unless-stopped \
  yourusername/papermind:latest 