#!/bin/bash

set -e

Public_IP=$1

echo "Waiting for 30 seconds to allow the server to start..."
sleep 30

# Function to make API calls
call_api() {
    method=$1
    endpoint=$2
    data=$3
    curl -s -X $method -H "Content-Type: application/json" -d "$data" -c cookies.txt -b cookies.txt http://${Public_IP}:80$endpoint
}

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "jq is not installed. Please install jq to run this script."
        exit 1
    fi
}

# Check if jq is installed
check_jq

# Check if server is up
if [ "$(curl -s -o /dev/null -w "%{http_code}" http://${Public_IP}:80)" == "200" ]; then
    echo "Web server is up!"

    # Login
    login_response=$(curl -s -X POST -c cookies.txt -b cookies.txt -H "Content-Type: application/x-www-form-urlencoded" -d "username='test'&password='test'" http://${Public_IP}:80/login)
    if [[ $login_response == *"Invalid username or password"* ]]; then
        echo "Login failed. Exiting."
        exit 1
    fi
    echo "Logged in successfully"

    # Create a horse
    create_response=$(call_api POST /add_horse '{"name":"TestHorse","image":"test.jpg","info":"Test horse"}')
    horse_id=$(echo $create_response | jq -r '.id')
    if [ -z "$horse_id" ] || [ "$horse_id" == "null" ]; then
        echo "Failed to create horse. Response: $create_response"
        exit 1
    fi
    echo "Created horse with ID: $horse_id"

    # Get the horse
    get_response=$(call_api GET /get_horse/$horse_id)
    if [[ $get_response == *"Horse not found"* ]]; then
        echo "Failed to retrieve horse. Response: $get_response"
        exit 1
    fi
    echo "Retrieved horse: $get_response"

    # Add a chore
    chore_response=$(call_api POST /add_chore '{"name":"TestChore","category":"day_opening","assign_all":false,"horse_ids":["'$horse_id'"]}')
    chore_id=$(echo $chore_response | jq -r '.id')
    if [ -z "$chore_id" ] || [ "$chore_id" == "null" ]; then
        echo "Failed to add chore. Response: $chore_response"
        exit 1
    fi
    echo "Added chore: $chore_response"

    # Update chore (mark as completed)
    update_response=$(call_api POST /update_chore '{"horse_id":"'$horse_id'","chore_id":"'$chore_id'","completed":true}')
    if [[ $(echo $update_response | jq -r '.success') != "true" ]]; then
        echo "Failed to update chore. Response: $update_response"
        exit 1
    fi
    echo "Updated chore successfully"

    # Get logs
    logs_response=$(call_api GET /get_logs)
    echo "Logs: $logs_response"

    # Remove the horse
    remove_response=$(call_api POST /remove_horse '{"horse_id":"'$horse_id'"}')
    if [[ $remove_response != *"Horse deleted successfully"* ]]; then
        echo "Failed to remove horse. Response: $remove_response"
        exit 1
    fi
    echo "Removed horse"

    # Verify removal
    get_response=$(call_api GET /get_horse/$horse_id)
    if [[ $get_response == *"Horse not found"* ]]; then
        echo "Horse successfully removed"
    else
        echo "Error: Horse not properly removed. Response: $get_response"
        exit 1
    fi

    echo "All tests passed successfully!"
else
    echo "Web server is down or not responding correctly."
    exit 1
fi
