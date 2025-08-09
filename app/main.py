from .services import parse_timeseries_data

if __name__ == "__main__":
    df = parse_timeseries_data("test_files/3_col_data.xlsx")
    print(df)
