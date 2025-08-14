from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from app.services import process_timeseries_data_at_different_freq

router = APIRouter()


@router.post(
    "/filler",
    tags="Filler",
    description="Gap Filler with ML algorithm to fill gaps in a timeseries data",
    status_code=status.HTTP_201_CREATED,
)
async def gap_filler_timeseries_data(
    timeseries_file: Annotated[UploadFile, File()],
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
    print(df)

    return {"message": "Success"}
