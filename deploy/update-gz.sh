cd /home/ec2-user/tokyo
git stash
git pull --rebase
git stash pop
make install
sudo /usr/local/bin/supervisorctl restart tokyo
