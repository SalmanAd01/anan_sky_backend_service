create device types

```
curl -X POST http://localhost:8001/device-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TemperatureDevice",
    "attributes": {
      "temperature": {
        "type": "integer",
        "required": true
      },
      "pressure": {
        "type": "integer",
        "required": false
      }
    }
  }'
```


get device types

```
curl -X GET http://localhost:8001/device-types
```


create devices (make sure to replace device_type_id with the actual ID obtained from the previous step)

```
curl -X POST http://localhost:8001/devices \  
  -H "Content-Type: application/json" \
  -d '{
    "device_type_id": "697c6bc5ba3230cbe73c5061",
    "name": "Boiler Sensor 1",
    "device_code": "DEV-001",
    "communication_type": "rest",
    "device_url": "http://localhost:9001"
  }'
```

get devices

```
curl -X GET http://localhost:8001/devices
```

create alert rule (make sure to replace device_id with the actual ID obtained from the previous step)

```
curl -X POST http://localhost:8001/device-alert-rules \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "697c6cafba3230cbe73c5062",
    "name": "HIGH_TEMPERATURE",
    "condition": "temperature > 80",
    "severity": "HIGH"
  }'

```

get alerts rules

```
curl -X GET http://localhost:8001/device-alert-rules
```

get alerts

```
curl -X GET http://localhost:8001/alerts
```


create external source type

```
curl -X POST http://localhost:8001/external-source-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather api",
    "attributes": {
      "temperature_high": { "type": "integer", "required": true },
      "temperature_low": { "type": "integer", "required": true },
      "conditions": { "type": "string", "required": true },
      "wind_speend": { "type": "integer", "required": true },
      "sunrise": { "type": "string", "required": true },
      "sunset": { "type": "string", "required": true }
    }
  }'
```

get external source types

```
curl -X GET http://localhost:8001/external-source-types
```