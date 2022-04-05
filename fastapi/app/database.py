import motor.motor_asyncio
from .models import Trip, Vehicle
import os
from urllib.parse import quote_plus


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
collection = database["vehicle"]

async def fetch_one_vehicle(serial):
    document = await collection.find_one({"serial": serial})
    return document

async def fetch_all_vehicles():
    vehicles = []
    cursor = collection.find({})
    async for document in cursor:
        vehicles.append(Vehicle(**document))
    return vehicles

async def create_vehicle(vehicle):
    document = vehicle
    result = await collection.insert_one(document)
    return document


async def update_vehicle(serial: str, **kwargs):
    await collection.update_one({"serial": serial}, 
    {"$set": kwargs})
    # {"title":title,
    # "description": desc,
    # "owner": owner,
    # "vehicle_type": vehicle_type,
    # "active": active}})
    document = await collection.find_one({"serial": serial})
    return document

async def remove_vehicle(serial):
    await collection.delete_one({"serial": serial})
    return True

