import json
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime

def response_from_string(string):
    return JSONResponse(json.loads(string))

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
