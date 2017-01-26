cd /home/ec2-user/tokyo
git stash
git pull --rebase
git stash pop
PYTHON3=/usr/bin/python3 make install
sudo /usr/local/bin/supervisorctl restart tokyo
