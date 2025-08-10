from .services import (
    check_frequency,
    check_minimum_data_to_process,
    parse_timeseries_data,
    predict_gaps_on_timeseries_data,
    resampling_data_based_on_freq,
)

if __name__ == "__main__":
    # NOTE: here we guarantee no nan value, is sorted and no duplicates
    df = parse_timeseries_data("test_files/data-30-min-miss-data.xlsx")
    min_data = check_minimum_data_to_process(df)

    if min_data:
        timedelta = check_frequency(df)
        if timedelta:
            pre_process_df = df.set_index("datetime")
            df_resampled = resampling_data_based_on_freq(df=pre_process_df, td=timedelta)
            new_df = predict_gaps_on_timeseries_data(df=df_resampled, target_column="energy")
            default_resample = resampling_data_based_on_freq(df=new_df, td="15min")
            default_15min_df = default_resample.interpolate(method="linear")
