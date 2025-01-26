import pandas as pd


def load_data(file: str):
    """Loads data from an Excel file obtained from PropReports > Executions.

    Adds the data to a DataFrame and reverses the order (so that it goes from the first trade of the session to the last).

    :param file: Path of the xls file to import.
    :return df: DataFrame with the file data.
    """
    df = pd.read_excel(file, engine='calamine')
    return df


def clean_data(df):
    """Clean the DataFrame: replace NaN with 0.
    """
    unwanted_columns = ['Fill Id', 'Currency', 'Status', 'Date', 'Clr', 'Misc']

    # Remove unwanted columns
    df = df.drop(columns=[col for col in unwanted_columns if col in df.columns])

    # Replace NaN with 0.
    df = df.fillna(0)

    # Format date and time.
    if 'Date/Time' in df.columns:
        df['Date/Time'] = pd.to_datetime(df['Date/Time'], format='%m/%d/%y %H:%M:%S')
        df['Date'] = df['Date/Time'].dt.date  # Column created for calculations grouped by day.

    # Reverse the order
    df = df.iloc[::-1]
    return df
