from db_models import DeviceTypeModel, DeviceModel
SERVER_URL = "http://localhost:8001/telemetry"

# after every 60s it will fetch data devices from DeviceModel get it's attribute from DeviceTypeModel and then it will generate random data based on attribute and send post request to above SERVER_URL /external-source/{source_id}/data to get data and print it.
import asyncio
import httpx
import random
from bson import ObjectId
from datetime import datetime
from db_models import DeviceModel, DeviceTypeModel


async def fetch_device_data():
    async with httpx.AsyncClient() as client:
        while True:
            async for device in DeviceModel.connect().find():
                device_type = await DeviceTypeModel.connect().find_one({"_id": ObjectId(device["device_type_id"])})
                if not device_type:
                    continue
                attributes = device_type.get("attributes", {})
                data = {}
                for attr, schema in attributes.items():
                    if schema.get("type") == "integer":
                        min_val = schema.get("min", 0)
                        max_val = schema.get("max", 1000)
                        data[attr] = random.randint(min_val, max_val)
                    elif schema.get("type") == "string":
                        random_str = f"str_{random.randint(1000, 9999)}"
                        data[attr] = random_str
                    if schema.get("required") == True:
                        continue
                    elif schema.get("required") == False and random.choice([True, False]) == False:
                        data.pop(attr, None)
                    # Add more types as needed
                payload = {
                    "device_id": str(device["_id"]),
                    "data": data,
                    "telemetry_sent_on": datetime.utcnow().isoformat(),
                }
                try:
                    response = await client.post(f"{SERVER_URL}", json=payload)
                    print(f"Sent data for device {device['_id']}: {response.status_code}")
                except Exception as e:
                    print(f"Error sending data for device {device['_id']}: {e}")
            await asyncio.sleep(60)  # wait for 60 seconds before next fetch
asyncio.run(fetch_device_data())



