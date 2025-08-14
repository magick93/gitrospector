# Gitrospector

A FastAPI-based application that analyzes GitHub repositories and extracts code structure information using the blarify library. This tool helps developers understand code architecture by generating graph representations of code relationships.

## Features

- Analyze GitHub repositories via API
- Extract code structure and relationships
- Generate graph representations of code architecture
- FastAPI-powered REST API
- Docker containerization for easy deployment

## Prerequisites

Before running the application, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29 or higher)
- Git (for cloning repositories)

## Setup Instructions

### Building the Docker Image

To build the Docker image from scratch, run the following command in the project root directory:

```bash
docker build -t gitrospector .
```

This command will:
- Use the Python 3.9 slim base image
- Install all dependencies from `requirements.txt`
- Copy the application code into the container
- Expose port 8000 for the API

### Running with Docker Compose

The recommended way to run the application is using Docker Compose:

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

   This will:
   - Build the Docker image (if not already built)
   - Start the container in detached mode
   - Map port 8000 from the container to your host machine
   - Automatically restart the container unless stopped

2. **Check the status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Basic Usage

Once the application is running, you can access it at `http://localhost:8000`.

### Health Check

To verify the application is running, make a GET request to the root endpoint:

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "GitHub Repository Analysis API"
}
```

### Analyzing a Repository

To analyze a GitHub repository, send a POST request to the `/analyze` endpoint:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/username/repository.git"
  }'
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "nodes": [
      {
        "id": "node_id",
        "properties": {
          "name": "component_name",
          "type": "component_type"
        }
      }
    ],
    "relationships": [
      {
        "id": "relationship_id",
        "source": "source_node_id",
        "target": "target_node_id",
        "type": "relationship_type"
      }
    ]
  }
}
```

## Environment Variables

The application uses the following environment variables, which should be configured in the `.env` file:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEO4J_URI` | Neo4j database connection URI | Yes | - |
| `NEO4J_USERNAME` | Neo4j database username | Yes | - |
| `NEO4J_PASSWORD` | Neo4j database password | Yes | - |
| `NEO4J_DATABASE` | Neo4j database name | Yes | `neo4j` |
| `AURA_INSTANCEID` | Neo4j Aura instance ID | Yes | - |
| `AURA_INSTANCENAME` | Neo4j Aura instance name | Yes | - |
| `PYTHONUNBUFFERED` | Python output buffering | No | `1` |

### Environment Configuration

The application requires Neo4j database connectivity for storing and querying graph data. Make sure to:

1. Copy the example environment variables:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual Neo4j credentials:
   ```
   NEO4J_URI=neo4j+s://your-neo4j-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   NEO4J_DATABASE=neo4j
   AURA_INSTANCEID=your-instance-id
   AURA_INSTANCENAME=your-instance-name
   ```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   If port 8000 is already in use, you can modify the port mapping in `docker-compose.yml`:
   ```yaml
   ports:
     - "8001:8000"  # Change to any available port
   ```

2. **Docker Build Failures**
   If the build fails, ensure you have the latest Docker version and try:
   ```bash
   docker-compose build --no-cache
   ```

3. **Repository Cloning Issues**
   The application requires internet access to clone GitHub repositories. Ensure your Docker container has network access.

4. **Neo4j Connection Issues**
   Verify your Neo4j credentials in the `.env` file and ensure the database is accessible from the container.

### Logs and Debugging

To troubleshoot issues:

1. View container logs:
   ```bash
   docker-compose logs app
   ```

2. Run the container interactively for debugging:
   ```bash
   docker-compose run --rm app bash
   ```

3. Check container status:
   ```bash
   docker-compose ps
   ```

### Performance Considerations

- Large repositories may take longer to analyze
- Ensure sufficient disk space for temporary repository cloning
- Monitor memory usage for large codebases

## API Reference

### Endpoints

- `GET /` - Health check endpoint
- `POST /analyze` - Analyze a GitHub repository

### Request Format (POST /analyze)

```json
{
  "github_url": "https://github.com/username/repository.git"
}
```

### Response Format

Success response:
```json
{
  "status": "success",
  "data": {
    "nodes": [...],
    "relationships": [...]
  }
}
```

Error response:
```json
{
  "status": "error",
  "message": "Error description"
}
```

## License

This project is licensed under the terms of the LICENSE file.