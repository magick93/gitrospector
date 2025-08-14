import os
import tempfile
import shutil
import re
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from git import Repo
from blarify import GraphBuilder

app = FastAPI()

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
                repo = Repo.clone_from(github_url, temp_dir)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to clone repository: {str(e)}")
            
            # Analyze the repository using blarify
            try:
                graph_builder = GraphBuilder(temp_dir)
                graph = graph_builder.build()
                
                # Extract nodes and relationships
                nodes = []
                relationships = []
                
                # Convert graph data to the required format
                # This assumes the graph object has nodes and relationships attributes
                # Adjust according to blarify's actual API
                if hasattr(graph, 'nodes'):
                    nodes = [{"id": node.id, "properties": node.properties} for node in graph.nodes]
                
                if hasattr(graph, 'relationships'):
                    relationships = [
                        {
                            "id": rel.id,
                            "source": rel.source_node.id,
                            "target": rel.target_node.id,
                            "type": rel.type
                        } for rel in graph.relationships
                    ]
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "data": {
                            "nodes": nodes,
                            "relationships": relationships
                        }
                    }
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Blarify analysis failed: {str(e)}")
        
        finally:
            # Clean up the temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Warning: Failed to clean up temporary directory: {str(e)}")
    
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"status": "error", "message": he.detail}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/")
async def root():
    return {"message": "GitHub Repository Analysis API"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)