from fastapi import FastAPI, HTTPException, Path
from typing import List
import os
from urllib.parse import quote_plus
from fastapi.middleware.cors import CORSMiddleware
from .models import CheckBeforeFinish, FinishTrip, Vehicle, UpdateVehicle, Trip, Position
from typing import Optional
from fastapi_mqtt import FastMQTT, MQTTConfig
import uuid
import json


from .database import (
    check_before_finish,
    fetch_one_vehicle,
    fetch_all_vehicles,
    create_vehicle,
    remove_trip,
    update_vehicle,
    remove_vehicle,
    fetch_all_vehicles_vehicle_ids,
    create_trip,
    fetch_all_trips,
    finish_trip,
    fetch_one_trip,
    remove_trip,
    save_current_position
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
    print(type(topic))
    if "trip" in topic:
        
        print("position data")
        message = json.loads(payload.decode())
        await save_current_position(message)
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
    response = await fetch_all_vehicles_vehicle_ids()
    for item in response:
        vehicle_id = item["vehicle_id"]
        topic = f"vehicle/{vehicle_id}/#"
        fast_mqtt.client.subscribe(topic)   
    return response

@app.get("/api/vehicle")
async def get_vehicles():
    response = await fetch_all_vehicles()
    return response

@app.get("/api/vehicle/{vehicle_id}", response_model=Vehicle)
async def get_vehicle_by_id(vehicle_id: uuid.UUID = Path(None, description="The vehicle_id of the Vehicle")):
    response = await fetch_one_vehicle(vehicle_id)
    if response:
        vehicle_id = response["vehicle_id"]
        topic = f"vehicle/{vehicle_id}/#"
        fast_mqtt.client.subscribe(topic) 
        return response
    raise HTTPException(404, f"There is no vehicle with the vehicle_id {vehicle_id}")

@app.post("/api/vehicle/", response_model=Vehicle)
async def create_one_vehicle(vehicle: Vehicle):
    response = await create_vehicle(vehicle.dict())
    vehicle_id = vehicle.dict()["vehicle_id"]
    if response:
        topic = f"vehicle/{vehicle_id}/#"
        fast_mqtt.client.subscribe(topic)  
        return response
    raise HTTPException(400, "Something went wrong")

@app.patch("/api/vehicle/{vehicle_id}/", response_model=Vehicle)
async def update_one_vehicle(vehicle_id: uuid.UUID, vehicle: UpdateVehicle):
    update_data = vehicle.dict(exclude_unset=True)
    response = await update_vehicle(vehicle_id, **update_data)
    if response:
        return response
    raise HTTPException(404, f"There is no Vehicle with the vehicle_id {vehicle_id}")

@app.delete("/api/vehicle/{vehicle_id}")
async def delete_vehicle(vehicle_id: uuid.UUID):
    response = await remove_vehicle(vehicle_id)
    if response:
        return "Successfully deleted vehicle"
    raise HTTPException(404, f"There is no todo with the title {vehicle_id}")


@app.get("/api/vehicle/check/{vehicle_id}")
async def check_vehicles(vehicle_id: uuid.UUID):
    fast_mqtt.publish(f"vehicle/{vehicle_id}/check", "Hello from Fastapi")
    
    return {"result": True,"message":"Published" }


@app.post("/api/trip/", response_model=Trip)
async def create_a_trip(trip: Trip):
    trip_dics = trip.dict()
    vehicle_id = trip_dics["vehicle_id"]
    topic = f"vehicle/{vehicle_id}/#"
    fast_mqtt.client.subscribe(topic)
    vehicle = await fetch_one_vehicle(vehicle_id)
    if vehicle:
        trip_dics["start_km"] = vehicle["current_km"]
        response = await create_trip(trip_dics)
        if response:
            return response
        raise HTTPException(400, "Something went wrong")
    raise HTTPException(404, f"Vehicle with the vehicle_id {vehicle_id} doesn't exist.")


@app.get("/api/trips/")
async def get_trips():
    response = await fetch_all_trips()
    return response

@app.get("/api/trips/{trip_id}/finish/", response_model=CheckBeforeFinish)
async def before_finish_trip(trip_id: uuid.UUID):
    response = await check_before_finish(trip_id)
    return response

@app.patch("/api/trip/{trip_id}/save/", response_model=Trip)
async def finish_and_save_trip(trip_id: uuid.UUID, finished_trip: FinishTrip):
    update_data = finished_trip.dict(exclude_unset=True)
    response = await finish_trip(trip_id, **update_data)
    if response:
        return response
    raise HTTPException(404, f"There is no Vehicle with the vehicle_id {trip_id}")


@app.delete("/api/trip/{trip_id}")
async def delete_trip(trip_id: uuid.UUID):
    response = await remove_trip(trip_id)
    if response:
        return "Successfully deleted trip"
    raise HTTPException(404, f"There is no todo with the title {trip_id}")


@app.get("/api/trip/{trip_id}", response_model=Trip)
async def get_trip_by_id(trip_id: uuid.UUID):
    response = await fetch_one_trip(trip_id)
    if response:
        return response
    raise HTTPException(404, f"There is no trip with id {trip_id}")