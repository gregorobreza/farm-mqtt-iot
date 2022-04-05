from typing import Optional, List, Literal
from pydantic import BaseModel, Field
import datetime
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
    # start: datetime.datetime
    # end: Optional[datetime.datetime] = None
    # duration: Optional[datetime.timedelta] = None
    distance: Optional[float] = None
    reason: str
    vehicle_serial: int


class Vehicle(BaseModel):
    serial: str
    title: str
    description: Optional[str] = None
    owner: str
    vehicle_type: Literal["electric", "diesel", "petrol"]
    active: bool

