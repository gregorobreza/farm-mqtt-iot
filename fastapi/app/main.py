from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
import os
from urllib.parse import quote_plus
from fastapi.middleware.cors import CORSMiddleware
from .models import Vehicle, Trip, Positions
from typing import Optional


from .database import (
    fetch_one_vehicle,
    fetch_all_vehicles,
    create_vehicle,
    update_vehicle,
    remove_vehicle,
)


origins = [
    "http://0.0.0.0:3000",
    "http://localhost:3000"
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get("/api/vehicle")
async def get_vehicles():
    response = await fetch_all_vehicles()
    return response

@app.get("/api/vehicle/{serial}", response_model=Vehicle)
async def get_vehicle_by_title(serial: str):
    response = await fetch_one_vehicle(serial)
    if response:
        return response
    raise HTTPException(404, f"There is no vehicle with the serial {serial}")

@app.post("/api/vehicle/", response_model=Vehicle)
async def create_one_vehicle(vehicle: Vehicle):
    response = await create_vehicle(vehicle.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")

@app.put("/api/todo/{serial}/", response_model=Vehicle)
async def update_one_vehicle(serial: str, title: Optional[str] = None, description: Optional[str] = None):
    para = {"title": title, "description": description}
    response = await update_vehicle(serial, **para)
    if response:
        return response
    raise HTTPException(404, f"There is no Vehicle with the serial {serial}")

@app.delete("/api/vehicle/{serial}")
async def delete_vehicle(serial: str):
    response = await remove_vehicle(serial)
    if response:
        return "Successfully deleted vehicle"
    raise HTTPException(404, f"There is no todo with the title {serial}")