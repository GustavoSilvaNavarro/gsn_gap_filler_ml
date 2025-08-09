from .services import (
    check_frequency,
    check_minimum_data_to_process,
    parse_timeseries_data,
    plotting_data,
    resampling_data_based_on_freq,
)

if __name__ == "__main__":
    # NOTE: here we guarantee no nan value, is sorted and no duplicates
    df = parse_timeseries_data("test_files/data-30-min-miss-data.xlsx")
    min_data = check_minimum_data_to_process(df)

    if min_data:
        timedelta = check_frequency(df)
        if timedelta:
            df_resampled = resampling_data_based_on_freq(df=df, td=timedelta)
            plotting_data(df=df_resampled)
