import os
import tempfile
import shutil
import re
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from git import Repo
from blarify.prebuilt.graph_builder import GraphBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="GitRospector API Documentation",
        version="1.0.0",
        description="API for analyzing GitHub repositories using Blarify",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={
            "dom_id": "#swagger-ui",
            "deepLinking": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "filter": True,
            "persistAuthorization": True,
        },
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

def is_valid_github_url(url):
    """Check if the URL is a valid GitHub repository URL"""
    pattern = r'^https://github\.com/[^/]+/[^/]+\.git$'
    return re.match(pattern, url) is not None

@app.post("/analyze")
async def analyze_github_repo(request: Request):
    try:
        data = await request.json()
        github_url = data.get("github_url")
        
        # Validate GitHub URL
        if not github_url:
            raise HTTPException(status_code=400, detail="GitHub URL is required")
        
        if not is_valid_github_url(github_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub URL format")
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clone the repository
            try:
                logger.info(f"Attempting to clone repository from {github_url} to {temp_dir}")
                repo = Repo.clone_from(github_url, temp_dir)
                logger.info(f"Successfully cloned repository from {github_url}")
            except Exception as e:
                logger.error(f"Failed to clone repository from {github_url}: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Failed to clone repository: {str(e)}")
            
            # Analyze the repository using blarify
            try:
                logger.info(f"Initializing GraphBuilder with directory: {temp_dir}")
                graph_builder = GraphBuilder(temp_dir)
                logger.info(f"GraphBuilder initialized with config: {graph_builder.config if hasattr(graph_builder, 'config') else 'No config found'}")
                
                logger.info("Building graph from repository...")
                graph = graph_builder.build()
                logger.info(f"Graph building completed. Graph object type: {type(graph)}")
                logger.debug(f"Graph object attributes: {dir(graph)}")
                
                # Extract nodes and relationships
                nodes_list = []
                relationships_list = []
                
                # Convert graph data to the required format
                if hasattr(graph, 'nodes'):
                    logger.info(f"Graph has {len(graph.nodes)} raw nodes")
                    nodes = [{"id": node.id, "properties": node.properties} for node in graph.nodes]
                    logger.info(f"Extracted {len(nodes)} nodes from graph")
                    if nodes:
                        logger.debug(f"First node sample: {nodes[0]}")
                
                if hasattr(graph, 'relationships'):
                    logger.info(f"Graph has {len(graph.relationships)} raw relationships")
                    relationships = [
                        {
                            "id": rel.id,
                            "source": rel.source_node.id,
                            "target": rel.target_node.id,
                            "type": rel.type
                        } for rel in graph.relationships
                    ]
                    
                    logger.info(f"Extracted {len(relationships)} relationships from graph")
                    if relationships:
                        logger.debug(f"First relationship sample: {relationships[0]}")
                
                if not nodes and not relationships:
                    logger.warning("No nodes or relationships found in graph")
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "data": {
                            "nodes": nodes_list,
                            "relationships": relationships_list
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Blarify analysis failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Blarify analysis failed: {str(e)}")
        
        finally:
            # Clean up the temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                # Log the error but don't fail the request
                logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")
    
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"status": "error", "message": he.detail}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
            logger.error(f"Unexpected error processing request: {str(e)}")
        )

@app.get("/")
async def root():
    return {"message": "GitHub Repository Analysis API"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)