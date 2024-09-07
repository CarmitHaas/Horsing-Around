#!/bin/bash

set -e

echo "Starting E2E tests..."

# Function to make API calls
call_api() {
    method=$1
    endpoint=$2
    data=$3
    curl -s -X $method -H "Content-Type: application/json" -d "$data" -c cookies.txt -b cookies.txt http://nginx:80$endpoint
}

wait_for_service() {
    echo "Waiting for service to be ready..."
    for i in {1..30}; do
        if curl -s http://nginx:80 > /dev/null; then
            echo "Service is ready!"
            return 0
        fi
        echo "Waiting for service to be ready... attempt $i"
        sleep 2
    done
    echo "Service did not become ready in time."
    return 1
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
wait_for_service

# Check if server is up
if [ "$(curl -s -o /dev/null -w "%{http_code}" http://nginx:80)" == "200" ]; then
    echo "Web server is up!"

    # Login
    login_response=$(curl -s -X POST -c cookies.txt -b cookies.txt -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin" http://nginx:80/login)
    if [[ $login_response == "Invalid username or password" ]]; then
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

    # Rest of your E2E test logic...

    echo "All tests passed successfully!"
else
    echo "Web server is down or not responding correctly."
    exit 1
fi