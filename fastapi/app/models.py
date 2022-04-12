from typing import Optional, List, Literal, Dict
from pydantic import BaseModel, Field
from datetime import datetime 
import uuid




class Position(BaseModel):
    # latitude: float
    # longitude: float
    # altitude: float
    # accuracy: float
    # speed: float
    # vertical_accuracy: float
    # bearing: float
    # elapsedMs: int
    # provider: str
    test_position: float
    timestamp : datetime 
    trip_id: uuid.UUID

class CheckBeforeFinish(BaseModel):
    trip_id: uuid.UUID
    duration: float
    trip_distance: float
    end_km: float


class FinishTrip(BaseModel):
    trip_id: uuid.UUID
    end: datetime = Field(default_factory=datetime.utcnow)
    end_km: Optional[float] = None

class Trip(BaseModel):
    trip_id : uuid.UUID = Field(default_factory=uuid.uuid4)
    start: datetime = Field(default_factory=datetime.utcnow)
    end: Optional[datetime] = None
    #duration: Optional[timedelta] = None
    start_km: Optional[float] = None
    end_km: Optional[float] = None 
    distance: Optional[float] = None
    reason: str
    first_name: str
    last_name: str
    vehicle_serial: str
    finished: bool = False

    class Config:
        allow_population_by_field_name = True


class Vehicle(BaseModel):
    serial: str
    title: str
    qr_code: Dict[str, str] 
    description: Optional[str] = None
    owner: str
    vehicle_type: Literal["electric", "diesel", "petrol"]
    active: bool
    current_km: float

class UpdateVehicle(BaseModel):
    title: Optional[str] = None
    qr_code: Dict[str, str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    vehicle_type: Optional[Literal["electric", "diesel", "petrol"]] = None
    active: Optional[bool] = None
    current_km: Optional[float] = None