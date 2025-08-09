from pandas import DataFrame
from sklearn.ensemble import RandomForestRegressor


def get_percentage_of_missing_data(df: DataFrame, missing_data_df: DataFrame) -> float:
    """Calculate the percentage of missing data in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The original DataFrame.
    missing_data_df : pandas.DataFrame
        DataFrame containing missing data.

    Returns
    -------
    float
        Percentage of missing data.
    """
    df_len = df.shape[0]
    missing_data_df = df.shape[1]
    return missing_data_df / df_len


def predict_gaps_on_timeseries_data(df: DataFrame, target_column: str = "energy") -> DataFrame:
    """Predict and fill gaps (missing values) in a time series DataFrame using a RandomForestRegressor.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame with a datetime index and a target column containing gaps (NaNs).
    target_column : str, optional
        Name of the column to fill gaps in (default is "energy").

    Returns
    -------
    pandas.DataFrame
        DataFrame with gaps in the target column filled by model predictions.

    Raises
    ------
    ValueError
        If the percentage of gaps to be filled exceeds 40%.
    """
    initial_df = df.copy()

    # Adding extra information to improve model prediction
    initial_df["hour"] = initial_df.index.hour
    initial_df["day_of_week"] = initial_df.index.dayofweek
    initial_df["month"] = initial_df.index.month
    initial_df["day_of_year"] = initial_df.index.dayofyear
    initial_df["time_since_start"] = (initial_df.index - initial_df.index[0]).total_seconds() / 3600
    initial_df["timestamp"] = initial_df.index

    # Splitting my data among training and prediction
    df_train = initial_df.dropna(subset=[target_column])
    df_predict = initial_df[initial_df[target_column].isna()]

    percentage = get_percentage_of_missing_data(df=initial_df, missing_data_df=df_predict)
    print(f"Total missing values is around {(percentage * 100):.2f} %")

    if percentage > 0.4:
        err_msg = "Gaps to filled exceed 40%, makes prediction much unreliable"
        raise ValueError(err_msg)

    # If there are no missing values to predict, just return the original DataFrame
    if df_predict.empty:
        return initial_df.drop(columns=initial_df.columns.difference(df.columns))

    features = ["hour", "day_of_week", "month", "day_of_year", "time_since_start"]
    x_train = df_train[features]
    y_train = df_train[target_column]
    x_predict = df_predict[features]

    # Model training and prediction
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(x_train, y_train)

    # Prediction
    predicted_values = model.predict(x_predict)

    # Used the predicted data to fill gaps
    initial_df.loc[initial_df[target_column].isna(), target_column] = predicted_values

    # clean up dataframe
    return initial_df.drop(columns=[*features, "timestamp"])
