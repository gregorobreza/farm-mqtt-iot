import motor.motor_asyncio
from .models import Trip, Vehicle
import os
from urllib.parse import quote_plus
from fastapi import HTTPException


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
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(endpoint, port)
    return mongo_client
    
mongo_client = get_client()
database = mongo_client.VehicleTrips
vehicle_collection = database["vehicle"]
trip_collection = database["trip"]

async def fetch_one_vehicle(serial:str):
    document = await vehicle_collection.find_one({"serial": serial})
    return document

async def fetch_all_vehicles():
    vehicles = []
    cursor = vehicle_collection.find({})
    async for document in cursor:
        vehicles.append(Vehicle(**document))
    return vehicles

async def fetch_all_vehicles_serials():
    vehicles_serials = []
    cursor = vehicle_collection.find({}, {"serial":1, "_id":0})
    async for document in cursor:
        vehicles_serials.append(document)
    return vehicles_serials

async def create_vehicle(vehicle):
    serial = vehicle["serial"]
    exists = await vehicle_collection.find_one({"serial": serial})
    if exists:
        raise HTTPException(404, f"Vehicle with the serial {serial} already exists.")
    document = vehicle
    result = await vehicle_collection.insert_one(document)
    return document


async def update_vehicle(serial: str, **kwargs):
    await vehicle_collection.update_one({"serial": serial}, 
    {"$set": kwargs})
    if "serial" in kwargs.keys():
        serial = kwargs["serial"]
    document = await vehicle_collection.find_one({"serial": serial})
    return document

async def remove_vehicle(serial: str):
    await vehicle_collection.delete_one({"serial": serial})
    return True

async def create_trip(trip):
    vehicle_serial = trip["vehicle_serial"]
    trip_document = trip
    vehicle_document = await vehicle_collection.find_one({"serial": vehicle_serial})
    if vehicle_document:
        result = await trip_collection.insert_one(trip_document)
        return trip_document
    else:
        raise HTTPException(400, "Thers no car with that serial")
