import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta
from fastapi import UploadFile
from pandas import DataFrame, Timedelta

from app.adapters import logger
from app.server.errors import BadRequestError

from .gap_filler_model import predict_gaps_on_timeseries_data


def parse_timeseries_data(file: UploadFile, file_path: str) -> DataFrame:
    """Read a CSV or Excel file and process datetime columns based on a simplified set of rules.

    Args:
        file (UploadFile): The uploaded file object (.csv or .xlsx).
        file_path (str): The path to the input file (.csv or .xlsx).

    Returns:
        pd.DataFrame: The processed DataFrame with a single 'datetime' column,
        or None if an error occurs.

    Raises:
        TypeError: If the file format is not supported.
        ValueError: If the column count is invalid or a column cannot be converted to datetime.
    """
    if file_path.endswith(".csv"):
        df = pd.read_csv(file)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        err_msg = f"Unsupported file format -> {file_path}. Please provide a .csv or .xlsx file."
        raise TypeError(err_msg)

    num_columns = df.shape[1]
    df = df.dropna(axis=0, how="any")

    # NOTE: Handle date and time columns
    if num_columns == 3:
        date_col, time_col, _ = df.columns

        try:
            pd.to_datetime(df[date_col].iloc[0])
        except (pd.errors.ParserError, ValueError, TypeError) as err:
            err_msg = f"Error: The first column {time_col} is not a date"
            raise ValueError(err_msg) from err

        df["datetime"] = pd.to_datetime(df[date_col].astype(str) + " " + df[time_col].astype(str))
        df = df.drop(columns=[date_col, time_col])
    elif num_columns == 2:
        datetime_col, _ = df.columns

        df["datetime"] = pd.to_datetime(df[datetime_col])
        df = df.drop(columns=[datetime_col])
    else:
        err_msg = f"Invalid file format, file should only have 2 or 3 columns, current: {num_columns}"
        raise ValueError(err_msg)

    # Renaming energy column name
    old_energy_name = df.columns[0]
    df = df.rename(columns={old_energy_name: "energy"})
    df = df.sort_values(by="datetime", ascending=True)
    df = df.drop_duplicates(subset=["datetime"], keep="first")
    logger.info("👻 Data has been extracted and minimal processed has been added")
    return df[["datetime", "energy"]]


def check_minimum_data_to_process(df: DataFrame, freq: float) -> bool:
    """Check if the DataFrame contains at least one year of data.

    Parameters
    ----------
    df : DataFrame
        The DataFrame containing a 'datetime' column.
    freq : float
        The frequency in minutes between data points.

    Returns
    -------
    bool
        True if the maximum timestamp is at least one year after the minimum timestamp, False otherwise.
    """
    max_timestamp: pd.Timestamp = df["datetime"].max()
    min_timestamp: pd.Timestamp = df["datetime"].min()
    next_year = min_timestamp + relativedelta(months=4) - relativedelta(minutes=freq)

    return max_timestamp >= next_year


def check_frequency(df: DataFrame) -> dict[str, Timedelta | float]:
    """Determine the most frequent time interval (in minutes) between consecutive 'datetime' entries in the DataFrame.

    Parameters
    ----------
    df : DataFrame
        The DataFrame containing a 'datetime' column.

    Returns
    -------
    float or None
        The most frequent interval in minutes if it matches one of {5, 15, 30, 60}, otherwise None.

    Raises
    ------
    ValueError
        If the frequency is not one of the supported values {5, 15, 30, 60}.
    """
    time_diffs = df["datetime"].diff()

    # Find the most frequent difference
    most_frequent_time: Timedelta = time_diffs.mode()[0]
    frequency_in_minutes: float = most_frequent_time.total_seconds() / 60

    if frequency_in_minutes not in {5, 15, 30, 60}:
        err_msg = f"Current frequency is not supported -> freq: {frequency_in_minutes}"
        raise ValueError(err_msg)

    return {"freq_time": most_frequent_time, "freq": frequency_in_minutes}


def resampling_5min_freq_to_15min_req(df: DataFrame) -> DataFrame:
    """Resample a DataFrame from 5-minute frequency to 15-minute frequency by averaging.

    Parameters
    ----------
    df : DataFrame
        The DataFrame to be resampled.

    Returns
    -------
    DataFrame
        The resampled DataFrame with 15-minute frequency.
    """
    return df.resample("15min").mean()


def resampling_data_based_on_freq(df: DataFrame, td: Timedelta | str) -> DataFrame:
    """Resample the DataFrame based on the given time frequency.

    Parameters
    ----------
    df : DataFrame
        The DataFrame containing a 'datetime' column.
    td : Timedelta | str
        The time frequency to resample the data.

    Returns
    -------
    DataFrame
        The resampled DataFrame with a 'time' column.
    """
    return df.resample(td).asfreq()


def process_timeseries_data_at_different_freq(file: UploadFile, file_extension: str) -> DataFrame:
    """Process timeseries data at different frequencies, filling gaps and resampling as needed.

    Parameters
    ----------
    file : UploadFile
        The uploaded file object (.csv or .xlsx).
    file_extension : str
        The file extension indicating the type of file.

    Returns
    -------
    DataFrame
        The processed DataFrame resampled to the required frequency.

    Raises
    ------
    BadRequestError
        If the timeseries data is too short to process.
    """
    parsed_df = parse_timeseries_data(file=file, file_path=f".{file_extension}")

    freq = check_frequency(df=parsed_df)
    has_min_data = check_minimum_data_to_process(df=parsed_df, freq=freq["freq"])

    if not has_min_data:
        err_msg = "Timeseries data is to short, needs more data to process"
        raise BadRequestError(err_msg)

    pre_process_df = parsed_df.set_index("datetime")
    df_resampled = resampling_data_based_on_freq(df=pre_process_df, td=freq["freq_time"])
    new_df = predict_gaps_on_timeseries_data(df=df_resampled, target_column="energy")
    if freq["freq"] == 15:
        return new_df

    if freq["freq"] == 5:
        # NOTE: need to do a resampling by averaging
        return resampling_5min_freq_to_15min_req(df=new_df)

    default_resample = resampling_data_based_on_freq(df=new_df, td="15min")
    return default_resample.interpolate(method="linear")


def plotting_data(df: DataFrame, time_col_name: str, show: bool = True) -> None:
    """Plot energy consumption data over time.

    Parameters
    ----------
    df : DataFrame
        The DataFrame containing 'datetime' and 'energy' columns.
    time_col_name : str
        The name of the column containing time or datetime values.
    show : bool, optional
        Whether to display the plot (default is True).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(df[time_col_name], df["energy"])

    # Add labels and a title
    plt.xlabel("Timestamp")
    plt.ylabel("Energy")
    plt.title("Energy Consumption")
    plt.grid(visible=True)
    plt.tight_layout()

    if show:
        plt.show()
        plt.show()
        plt.show()
