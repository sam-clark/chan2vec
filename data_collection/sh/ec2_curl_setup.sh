mkdir python
rm -rf data
mkdir data
sudo apt-get update
sudo apt-get -y install python3-pip
pip3 install bs4
pip3 install requests
pip3 install boto3
touch /home/ubuntu/_SUCCESS
