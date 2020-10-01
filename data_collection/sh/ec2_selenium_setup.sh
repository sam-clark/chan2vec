mkdir python
rm -rf data
mkdir data
sudo apt-get update
sudo apt-get -y install python3-pip
sudo apt-get -y install unzip
pip3 install selenium
pip3 install pyvirtualdisplay
pip3 install boto3
# wget https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip
wget https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo apt -y install xvfb
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt -y install ./google-chrome-stable_current_amd64.deb
touch /home/ubuntu/_SUCCESS
