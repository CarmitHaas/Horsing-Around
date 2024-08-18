#!/bin/bash

# Function to import collection if it's empty
import_collection_if_empty() {
  local db=$1
  local collection=$2
  local file=$3

  count=$(mongosh --quiet --eval "db.getSiblingDB('$db').$collection.countDocuments()")

  if [ "$count" -eq "0" ]; then
    echo "Importing sample data into $collection collection..."
    mongoimport --db $db --collection $collection --file $file
  else
    echo "$collection collection already contains data."
  fi
}

# Import collections if they are empty
import_collection_if_empty "horsing_around" "chores" "/data/chores.json"
import_collection_if_empty "horsing_around" "horses" "/data/horses.json"