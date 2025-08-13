from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from app.server.errors import BadRequestError
from app.services import (
    check_frequency,
    check_minimum_data_to_process,
    parse_timeseries_data,
    predict_gaps_on_timeseries_data,
    resampling_data_based_on_freq,
)

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

    Raises
    ------
    BadRequestError
        If the timeseries data is too short to process.
    """
    file_extension = timeseries_file.filename.split(".")[-1].strip().lower()
    parsed_df = parse_timeseries_data(file=timeseries_file.file, file_path=f".{file_extension}")

    freq = check_frequency(df=parsed_df)
    has_min_data = check_minimum_data_to_process(df=parsed_df, freq=freq["freq"])

    if not has_min_data:
        err_msg = "Timeseries data is to short, needs more data to process"
        raise BadRequestError(err_msg)

    pre_process_df = parsed_df.set_index("datetime")
    df_resampled = resampling_data_based_on_freq(df=pre_process_df, td=freq["freq_time"])
    new_df = predict_gaps_on_timeseries_data(df=df_resampled, target_column="energy")
    default_resample = resampling_data_based_on_freq(df=new_df, td="15min")
    default_15min_df = default_resample.interpolate(method="linear")
    print(default_15min_df)

    return {"message": "Success"}
