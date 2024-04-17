#!/usr/bin/env bash
# Bash script that sets up your web servers for the deployment of web_static

# Install nginx
sudo apt-get -y update
sudo apt-get -y install nginx
sudo service nginx restart

# Directory/ File config
sudo mkdir -p /data/web_static/releases/test/ /data/web_static/shared/

# Test file
echo "Hello World!!" | sudo tee /data/web_static/releases/test/index.html > /dev/null

# Symbolic link
sudo ln -sf /data/web_static/releases/test/ /data/web_static/current

# File permissions
sudo chown -hR ubuntu:ubuntu /data/

# Configure nginx
sudo sed -i "44i \\\n\tlocation /hbnb_static {\n\t\talias /data/web_static/current/;\n\t}" /etc/nginx/sites-available/default

# restart Nginx
sudo service nginx restart
