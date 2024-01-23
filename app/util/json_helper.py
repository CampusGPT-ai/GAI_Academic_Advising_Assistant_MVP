import json
from fastapi.responses import JSONResponse

def response_from_string(string):
    return JSONResponse(json.loads(string))
