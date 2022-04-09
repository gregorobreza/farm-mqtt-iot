from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import date, datetime, time, timedelta
import uuid


class Positions(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    accuracy: float
    speed: float
    vertical_accuracy: float
    bearing: float
    elapsedMs: int
    provider: str
    trip_id: str


class Trip(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    duration: Optional[timedelta] = None
    distance: Optional[float] = None
    reason: str
    first_name: str
    last_name: str
    vehicle_serial: str


class Vehicle(BaseModel):
    serial: str
    title: str
    description: Optional[str] = None
    owner: str
    vehicle_type: Literal["electric", "diesel", "petrol"]
    active: bool

class UpdateVehicle(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    vehicle_type: Optional[Literal["electric", "diesel", "petrol"]] = None
    active: Optional[bool] = None