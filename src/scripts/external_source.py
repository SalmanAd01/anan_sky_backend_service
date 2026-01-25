from bson import ObjectId
from fastapi import APIRouter, FastAPI, HTTPException
import random
import datetime
from db_models import ExternalSourceTypeModel

app = FastAPI(title="External Source Simulator")


@app.get("/external-source/ping")
async def ping_external_source():
    return {"status": "external source route is working"}

@app.get("/external-source/{source_id}/data")
async def get_external_source_data(source_id: str, created_on: str = None):
    try:
        source_obj = await ExternalSourceTypeModel.connect().find_one({"_id": ObjectId(source_id)})
        if not source_obj:
            raise HTTPException(status_code=404, detail="external source type not found")

        # Generate random data for from source_obj attributes
        data = {}
        for attr_name, schema in source_obj.get("attributes", {}).items():
            if schema.get("type") == "integer":
                data[attr_name] = random.randint(schema.get("min", 0), schema.get("max", 100))
            elif schema.get("type") == "string":
                data[attr_name] = f"sample_{random.randint(1, 1000)}"
        return data
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scripts.external_source:app", host="127.0.0.1", port=8000, reload=True)