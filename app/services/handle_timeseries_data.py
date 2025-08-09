import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas import DataFrame


def parse_timeseries_data(file_path: str) -> DataFrame:
    """Read a CSV or Excel file and process datetime columns based on a simplified set of rules.

    Args:
        file_path (str): The path to the input file (.csv or .xlsx).

    Returns:
        pd.DataFrame: The processed DataFrame with a single 'datetime' column,
        or None if an error occurs.

    Raises:
        TypeError: If the file format is not supported.
        ValueError: If the column count is invalid or a column cannot be converted to datetime.
    """
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
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

        try:
            pd.to_datetime(df[datetime_col].iloc[0])
        except (pd.errors.ParserError, ValueError, TypeError) as err:
            err_msg = f"Error: {datetime_col} column cannot be converted to a datetime."
            raise ValueError(err_msg) from err

        df["datetime"] = pd.to_datetime(df[datetime_col])
        df = df.drop(columns=[datetime_col])
    else:
        err_msg = f"Invalid file format, file should only have 2 or 3 columns, current: {num_columns}"
        raise ValueError(err_msg)

    # Renaming energy column name
    old_energy_name = df.columns[0]
    df = df.rename(columns={old_energy_name: "energy"})
    return df[["datetime", "energy"]]


def check_minimum_data_to_process(df: DataFrame) -> bool:
    """Check if the DataFrame contains at least one year of data.

    Parameters
    ----------
    df : DataFrame
        The DataFrame containing a 'datetime' column.

    Returns
    -------
    bool
        True if the maximum timestamp is at least one year after the minimum timestamp, False otherwise.
    """
    max_timestamp: pd.Timestamp = df["datetime"].max()
    min_timestamp: pd.Timestamp = df["datetime"].min()
    next_year = min_timestamp + relativedelta(years=1) - relativedelta(minutes=15)

    return max_timestamp >= next_year


def check_frequency(df: DataFrame) -> float | None:
    """Determine the most frequent time interval (in minutes) between consecutive 'datetime' entries in the DataFrame.

    Parameters
    ----------
    df : DataFrame
        The DataFrame containing a 'datetime' column.

    Returns
    -------
    float or None
        The most frequent interval in minutes if it matches one of {5, 15, 30, 60}, otherwise None.
    """
    time_diffs = df["datetime"].diff()

    # Find the most frequent difference
    most_frequent_freq = time_diffs.mode()[0]
    frequency_in_minutes: float = most_frequent_freq.total_seconds() / 60

    if frequency_in_minutes in {5, 15, 30, 60}:
        return frequency_in_minutes
    return None
