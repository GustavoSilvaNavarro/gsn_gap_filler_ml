from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from app.services import parse_timeseries_data

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
):
    file_extension = timeseries_file.filename.split(".")[-1].strip().lower()
    parsed_df = parse_timeseries_data(file=timeseries_file.file, file_path=f".{file_extension}")
    print(parsed_df)

    return {"msg": "Hello World"}
