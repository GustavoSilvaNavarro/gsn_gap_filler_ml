from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncEngine

from app.connections import connections
from app.services import process_timeseries_data_at_different_freq, store_timeseries_data

router = APIRouter()


@router.post(
    "/filler",
    tags="Filler",
    description="Gap Filler with ML algorithm to fill gaps in a timeseries data",
    status_code=status.HTTP_201_CREATED,
)
async def gap_filler_timeseries_data(
    timeseries_file: Annotated[UploadFile, File()],
    engine: Annotated[AsyncEngine, Depends(connections.get_engine)],
    # file_details: Annotated[str, Form()],
) -> dict:
    """Fill gaps in a timeseries data file using a machine learning algorithm.

    Parameters
    ----------
    timeseries_file : UploadFile
        The uploaded timeseries data file.

    Returns
    -------
    dict
        A message indicating success.
    """
    file_extension = timeseries_file.filename.split(".")[-1].strip().lower()
    df = process_timeseries_data_at_different_freq(file=timeseries_file.file, file_extension=file_extension)
    await store_timeseries_data(df=df, engine=engine)

    return {"message": "Success"}
