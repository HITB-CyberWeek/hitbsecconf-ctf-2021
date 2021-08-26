#!/bin/sh

chown passman:passman /home/passman/data/
chown root:root /home/passman
chmod 755 /home/passman
chmod 700 /home/passman/data

cd /home/passman
exec su -c ./passman_server -s /bin/sh passman
