#!/bin/bash

# Make POST request and handle errors
response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/paperless-ngx/paperless-ngx.git"}')

# Extract status code and response body
http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | sed '$d')

# Validate response
if [[ $http_code -ne 200 ]]; then
  echo "Error: Request failed with status code $http_code" >&2
  echo "Response: $response_body" >&2
  exit 1
fi

# Format and output JSON response
echo "$response_body" | jq .