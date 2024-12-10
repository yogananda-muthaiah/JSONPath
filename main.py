from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import jsonpath_ng.ext

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class JSONPathRequest(BaseModel):
    json_input: str
    jsonpath_expr: str

@app.post("/evaluate_jsonpath/")
async def evaluate_jsonpath(request: JSONPathRequest):
    try:
        # Validate JSON input is not empty
        if not request.json_input.strip():
            raise HTTPException(status_code=400, detail="JSON input cannot be empty")
        
        # Parse the input JSON
        try:
            parsed_json = json.loads(request.json_input)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON input")
        
        # Validate JSON input is a valid JSON object
        if not isinstance(parsed_json, dict):
            raise HTTPException(status_code=400, detail="JSON input must be a valid JSON object")
        
        # Validate JSONPath expression is not empty
        if not request.jsonpath_expr.strip():
            raise HTTPException(status_code=400, detail="JSONPath expression cannot be empty")
        
        # Compile the JSONPath expression
        try:
            jsonpath_expr = jsonpath_ng.ext.parse(request.jsonpath_expr)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSONPath expression: {str(e)}")
        
        # Evaluate the JSONPath expression
        matches = [match.value for match in jsonpath_expr.find(parsed_json)]
        
        return {
            "matches": matches,
            "match_count": len(matches)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def serve_index(request: Request):
    return request.app.state.templates.TemplateResponse("index.html", {"request": request})

@app.get("/expressions")
async def serve_expressions(request: Request):
    return request.app.state.templates.TemplateResponse("expression.html", {"request": request})

# Initialize templates
app.state.templates = Jinja2Templates(directory="templates")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)