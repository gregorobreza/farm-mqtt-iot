from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
import os
from urllib.parse import quote_plus
from fastapi.middleware.cors import CORSMiddleware
from .models import Vehicle, UpdateVehicle, Trip, Positions
from typing import Optional
from fastapi_mqtt import FastMQTT, MQTTConfig


from .database import (
    fetch_one_vehicle,
    fetch_all_vehicles,
    create_vehicle,
    update_vehicle,
    remove_vehicle,
    fetch_all_vehicles_serials,
    create_trip
)


origins = [
    "http://0.0.0.0:3000",
    "http://localhost:3000"
]


app = FastAPI()
mqtt_config = MQTTConfig(host="mqtt-mosquitto",port=1883,ssl=False, username="gobreza", password="4064")
fast_mqtt = FastMQTT(config=mqtt_config)
fast_mqtt.init_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
    fast_mqtt.client.subscribe("bla") #subscribing mqtt topic
    print("Connected: ", client, flags, rc, properties)


@fast_mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ",topic, payload.decode(), qos, properties)
    return 0

@fast_mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")

@fast_mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get("/api/vehicle/connect")
async def subscribe_vehicles():
    response = await fetch_all_vehicles_serials()
    for item in response:
        serial = item["serial"]
        topic = f"vehicle/{serial}/#"
        fast_mqtt.client.subscribe(topic)   
    return response

@app.get("/api/vehicle")
async def get_vehicles():
    response = await fetch_all_vehicles()
    return response

@app.get("/api/vehicle/{serial}", response_model=Vehicle)
async def get_vehicle_by_title(serial: str = Path(None, description="The serial of the Vehicle")):
    response = await fetch_one_vehicle(serial)
    if response:
        return response
    raise HTTPException(404, f"There is no vehicle with the serial {serial}")

@app.post("/api/vehicle/", response_model=Vehicle)
async def create_one_vehicle(vehicle: Vehicle):
    response = await create_vehicle(vehicle.dict())
    serial = vehicle.dict()["serial"]
    if response:
        topic = f"vehicle/{serial}/#"
        fast_mqtt.client.subscribe(topic)  
        return response
    raise HTTPException(400, "Something went wrong")

@app.patch("/api/vehicle/{serial}/", response_model=Vehicle)
async def update_one_vehicle(serial: str, vehicle: UpdateVehicle):
    update_data = vehicle.dict(exclude_unset=True)
    response = await update_vehicle(serial, **update_data)
    if response:
        return response
    raise HTTPException(404, f"There is no Vehicle with the serial {serial}")

@app.delete("/api/vehicle/{serial}")
async def delete_vehicle(serial: str):
    response = await remove_vehicle(serial)
    if response:
        return "Successfully deleted vehicle"
    raise HTTPException(404, f"There is no todo with the title {serial}")


@app.get("/api/vehicle/check/{serial}")
async def check_vehicles(serial: str):
    fast_mqtt.publish(f"vehicle/{serial}/check", "Hello from Fastapi")
    
    return {"result": True,"message":"Published" }


@app.post("/api/trip/", response_model=Trip)
async def create_a_trip(trip: Trip):
    response = await create_trip(trip.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")