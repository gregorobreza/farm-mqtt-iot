from datetime import datetime
from tracemalloc import start
import motor.motor_asyncio
from .models import Trip, Vehicle, Position, CheckBeforeFinish
import os
from urllib.parse import quote_plus
from fastapi import HTTPException
from uuid import UUID
from bson.binary import UuidRepresentation
import pymongo


mongo_client = None

def get_client():
    """
    Setup a mongo client for the site
    :return:
    """
    global mongo_client
    if bool(mongo_client):
        return mongo_client
    host = os.getenv('MONGODB_HOST', '')
    username = os.getenv('MONGODB_USER', '')
    password = os.getenv('MONGODB_PASSWORD', '')
    port = int(os.getenv('MONGODB_PORT', 27017))
    endpoint = 'mongodb://{0}:{1}@{2}'.format(quote_plus(username),
                                              quote_plus(password), host)
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(endpoint, port, uuidRepresentation="standard")
    return mongo_client
    
mongo_client = get_client()
database = mongo_client.VehicleTrips
vehicle_collection = database["vehicle"]
trip_collection = database["trip"]
position_collection = database["position"]

async def fetch_one_vehicle(vehicle_id):
    document = await vehicle_collection.find_one({"vehicle_id": vehicle_id})
    return document

async def fetch_all_vehicles():
    vehicles = []
    cursor = vehicle_collection.find({})
    async for document in cursor:
        vehicles.append(Vehicle(**document))
    return vehicles

async def fetch_all_vehicles_vehicle_ids():
    vehicles_vehicle_ids = []
    cursor = vehicle_collection.find({}, {"vehicle_id":1, "_id":0})
    async for document in cursor:
        vehicles_vehicle_ids.append(document)
    return vehicles_vehicle_ids

async def create_vehicle(vehicle):
    vehicle_id = vehicle["vehicle_id"]
    exists = await vehicle_collection.find_one({"vehicle_id": vehicle_id})
    if exists:
        raise HTTPException(404, f"Vehicle with the vehicle_id {vehicle_id} already exists.")
    document = vehicle
    result = await vehicle_collection.insert_one(document)
    return document


async def update_vehicle(vehicle_id: str, **kwargs):
    await vehicle_collection.update_one({"vehicle_id": vehicle_id}, 
    {"$set": kwargs})
    if "vehicle_id" in kwargs.keys():
        vehicle_id = kwargs["vehicle_id"]
    document = await vehicle_collection.find_one({"vehicle_id": vehicle_id})
    return document

async def remove_vehicle(vehicle_id: str):
    await vehicle_collection.delete_one({"vehicle_id": vehicle_id})
    return True

async def create_trip(trip):
    vehicle_id = trip["vehicle_id"]
    trip_document = trip
    vehicle_document = await vehicle_collection.find_one({"vehicle_id": vehicle_id})
    if vehicle_document:
        result = await trip_collection.insert_one(trip_document)
        return trip_document
    else:
        raise HTTPException(400, "Thers no car with that vehicle_id")

async def fetch_all_trips():
    trips = []
    cursor = trip_collection.find({})
    async for document in cursor:
        trips.append(Trip(**document))
    return trips

async def fetch_one_trip(trip_id):
    document = await trip_collection.find_one({"trip_id": trip_id})
    return document

async def finish_trip(trip_id, **kwargs):
    trip = await trip_collection.find_one({"trip_id": trip_id})
    start = trip["start"]
    end = datetime.utcnow()
    kwargs["trip_distance"] = kwargs["end_km"] - trip["start_km"]
    kwargs["duration"] = (end - start).total_seconds()
    kwargs["finished"] = True
    kwargs["trip_id"] = trip_id
    kwargs["start"] = start
    kwargs["end"] = end
    print(kwargs)
    await trip_collection.update_one({"trip_id": trip_id}, {"$set": kwargs})
    document = await trip_collection.find_one({"trip_id": trip_id})
    return document

async def remove_trip(trip_id):
    await trip_collection.delete_one({"trip_id": trip_id})
    return True

async def save_current_position(position:Position):
    " TODO: Sproti racunaj in pristeval razdalje med tockami"
    trip_id = position["trip_id"]
    position_message = position
    position_message["trip_id"] = UUID(trip_id)
    position_message["timestamp"] = datetime.utcnow()
    trip_document = await trip_collection.find_one({"trip_id": UUID(trip_id)})
    if trip_document:
        result = await position_collection.insert_one(position_message)
        return True
    else:
        raise HTTPException(400, "There is no trip with that id. ")

async def check_before_finish(trip_id):
    #get trip insertion
    trip = await trip_collection.find_one({"trip_id": trip_id})
    start_km = trip["start_km"]
    first = position_collection.find({"trip_id": trip_id}).sort("_id",pymongo.ASCENDING).limit(1)
    last = position_collection.find({"trip_id": trip_id}).sort("_id",pymongo.DESCENDING).limit(1)
    first = await first.to_list(length=1)
    last = await last.to_list(length=1)
    # TODO: spremeni test position!!
    end_km = start_km + last[0]["test_position"]
    time = (last[0]["timestamp"] - first[0]["timestamp"]).total_seconds()
    return CheckBeforeFinish(**{"trip_id": trip_id, "duration": time, "trip_distance":last[0]["test_position"], "end_km":end_km})

