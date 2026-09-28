from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.body_measurement import BodyMeasurement
from app.schemas.body_measurement import (
    BodyMeasurementCreate,
    BodyMeasurementResponse,
)

router = APIRouter(
    prefix="/body-measurements",
    tags=["Body Measurements"]
)


@router.post(
    "/",
    response_model=BodyMeasurementResponse
)
def create_body_measurement(
    data: BodyMeasurementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    measurement = BodyMeasurement(
        user_id=current_user.id,
        weight_kg=data.weight_kg,
        body_fat_percent=data.body_fat_percent
    )

    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    return measurement


@router.get(
    "/me",
    response_model=list[BodyMeasurementResponse]
)
def get_my_body_measurements(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    measurements = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == current_user.id)
        .order_by(BodyMeasurement.created_at.desc())
        .all()
    )

    return measurements