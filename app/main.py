from .services import check_frequency, check_minimum_data_to_process, parse_timeseries_data

if __name__ == "__main__":
    df = parse_timeseries_data("test_files/3_col_data.xlsx")
    min_data = check_minimum_data_to_process(df)
    if min_data:
        check_frequency(df)
