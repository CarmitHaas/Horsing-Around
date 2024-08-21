#!/bin/bash

Public_IP=$1

echo "Waiting for 30 seconds to allow the server to start..."
sleep 30

if [ "$(curl -s -o /dev/null -w "%{http_code}" http://${Public_IP}:80)" == "200" ]; then
    echo "Web server is up!"
else
    echo "Web server is down or not responding correctly."
fi
