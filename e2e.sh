#!/bin/bash

Public_IP=$1

echo "Waiting for 30 seconds to allow the server to start..."
sleep 30

# Function to make API calls
call_api() {
    method=$1
    endpoint=$2
    data=$3
    curl -s -X $method -H "Content-Type: application/json" -d "$data" http://${Public_IP}:80$endpoint
}

# Check if server is up
if [ "$(curl -s -o /dev/null -w "%{http_code}" http://${Public_IP}:80)" == "200" ]; then
    echo "Web server is up!"

    # Create a horse
    create_response=$(call_api POST /add_horse '{"name":"TestHorse","image":"test.jpg","info":"Test horse"}')
    horse_id=$(echo $create_response | jq -r '.id')
    echo "Created horse with ID: $horse_id"

    # Get the horse
    get_response=$(call_api GET /get_horse/$horse_id)
    echo "Retrieved horse: $get_response"

    # Add a chore
    chore_response=$(call_api POST /add_chore '{"name":"TestChore","category":"day_opening","assign_all":false,"horse_ids":["'$horse_id'"]}')
    echo "Added chore: $chore_response"

    # Update chore (mark as completed)
    chore_id=$(echo $chore_response | jq -r '.id')
    call_api POST /update_chore '{"horse_id":"'$horse_id'","chore_id":"'$chore_id'","completed":true}'
    echo "Updated chore"

    # Get logs
    logs_response=$(call_api GET /get_logs)
    echo "Logs: $logs_response"

    # Remove the horse
    call_api POST /remove_horse '{"horse_id":"'$horse_id'"}'
    echo "Removed horse"

    # Verify removal
    get_response=$(call_api GET /get_horse/$horse_id)
    if [[ $get_response == *"Horse not found"* ]]; then
        echo "Horse successfully removed"
    else
        echo "Error: Horse not properly removed"
    fi

else
    echo "Web server is down or not responding correctly."
fi