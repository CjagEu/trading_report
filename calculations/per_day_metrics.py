from pandas import DataFrame
from calculations.row_calculations import get_trades_by_date


def calculate_gross_pnl_by_day(df: DataFrame):
    """Calculates the gross PnL by day.
    """
    df_by_day = {day: group for day, group in df.groupby('Date')}  # Convert the dataframe to a dictionary. Key: day, value: rows

    gross_pnl_by_day = {}

    for day, rows in df_by_day.items():
        # Create an entry in the dictionary for each day.
        gross_pnl_by_day[day] = 0

        # Get the unique symbols for the day.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # DataFrame filtered by Symbol.

            # Calculate the gross PnL, excluding commissions.
            calculation = ((symbol_row['Price'] * symbol_row['Qty']) * symbol_row['B/S'].apply(lambda x: -1 if x in ['B'] else 1)).sum()

            gross_pnl_by_day[day] += calculation

    return gross_pnl_by_day


def calculate_cumulative_gross_pnl_by_day(df: DataFrame):
    """Calculates the cumulative gross PnL by day from a DataFrame.
    """
    # Convert the DataFrame into a dictionary: key = day, value = rows for that day.
    df_by_day = {day: group for day, group in df.groupby('Date')}

    # Dictionary to store the cumulative PnL.
    cumulative_pnl_by_day = {}
    cumulative_pnl = 0  # Initialize the PnL accumulator.

    for day, rows in sorted(df_by_day.items()):  # Sort days chronologically.
        # Get the list of unique symbols traded on the day.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        daily_pnl = 0  # Gross PnL for the day.

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # Filter by symbol.

            # Calculate the gross PnL for the symbol.
            calculation = ((symbol_row['Price'] * symbol_row['Qty']) *
                           symbol_row['B/S'].apply(lambda x: -1 if x == 'B' else 1)).sum()

            daily_pnl += calculation

        cumulative_pnl += daily_pnl  # Update the accumulator.
        cumulative_pnl_by_day[day] = cumulative_pnl  # Save the accumulated PnL up to the current day.

    return cumulative_pnl_by_day


def calculate_net_pnl_by_day(df: DataFrame):
    """Calculates the net PnL by day.
    """
    df_by_day = {day: group for day, group in df.groupby('Date')}  # Convert the dataframe to a dictionary. Key: day, value: rows

    net_pnl_by_day = {}

    for day, rows in df_by_day.items():
        # Create an entry in the dictionary for each day.
        net_pnl_by_day[day] = 0

        # Get the unique symbols for the day.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # DataFrame filtered by Symbol.

            # Calculate the gross PnL, excluding commissions.
            calculation = ((symbol_row['Price'] * symbol_row['Qty']) * symbol_row['B/S'].apply(lambda x: -1 if x in ['B'] else 1)).sum()

            # Calculate commissions and ECN fees by summing per row
            commissions = symbol_row[['Comm', 'SEC', 'TAF', 'NSCC', 'CAT']].sum().sum()
            ecn_fees = symbol_row['Ecn Fee'].sum()

            # Adjust the PnL calculation with commissions and ECN fees
            calculation = calculation - commissions + ecn_fees * -1

            net_pnl_by_day[day] += calculation

    return net_pnl_by_day


def calculate_cumulative_net_pnl_by_day(df: DataFrame):
    """Calculates the cumulative net PnL by day from a DataFrame.
    """
    # Convert the DataFrame into a dictionary: key = day, value = rows for that day.
    df_by_day = {day: group for day, group in df.groupby('Date')}

    # Dictionary to store the cumulative PnL.
    cumulative_net_pnl_by_day = {}
    cumulative_pnl = 0  # Initialize the PnL accumulator.

    for day, rows in sorted(df_by_day.items()):  # Sort days chronologically.
        # Get the list of unique symbols traded on the day.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        daily_net_pnl = 0  # Net PnL for the day.

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # Filter by symbol.

            # Calculate the gross PnL for the symbol.
            calculation = ((symbol_row['Price'] * symbol_row['Qty']) *
                           symbol_row['B/S'].apply(lambda x: -1 if x == 'B' else 1)).sum()

            # Calculate commissions and ECN fees.
            commissions = symbol_row[['Comm', 'SEC', 'TAF', 'NSCC', 'CAT']].sum().sum()
            ecn_fees = symbol_row['Ecn Fee'].sum()

            # Adjust the PnL calculation with commissions and ECN fees.
            calculation = calculation - commissions + ecn_fees * -1

            daily_net_pnl += calculation

        cumulative_pnl += daily_net_pnl  # Update the accumulator.
        cumulative_net_pnl_by_day[day] = cumulative_pnl  # Save the accumulated net PnL up to the current day.

    return cumulative_net_pnl_by_day


def calculate_shares_by_day(df: DataFrame):
    """Calculates the shares traded by day.
    """
    df_by_day = {day: group for day, group in df.groupby('Date')}  # Convert the dataframe to a dictionary. Key: day, value: rows

    # Initialize the dictionary.
    shares_by_day = {}

    for day, rows in df_by_day.items():
        # Create an entry in the dictionary for each day.
        shares_by_day[day] = {'Buy': 0, 'Sell': 0, 'Short': 0}

        # Iterate over the rows of the DataFrame.
        for _, row in rows.iterrows():
            # Add to the corresponding key based on the 'B/S' value.
            if row['B/S'] == 'B':
                shares_by_day[day]['Buy'] += row['Qty']
            elif row['B/S'] == 'S':
                shares_by_day[day]['Sell'] += row['Qty']
            elif row['B/S'] == 'T':
                shares_by_day[day]['Short'] += row['Qty']

        # Ensure that the number of actions match.
        if shares_by_day[day]['Buy'] != shares_by_day[day]['Sell'] + shares_by_day[day]['Short']:
            raise ValueError(f"The total 'Buy' ({shares_by_day[day]['Buy']}) does not match the sum of 'Sell' ({shares_by_day[day]['Sell']}) and 'Short' ({shares_by_day[day]['Short']}) for the symbol {row['Symbol']}.")

    return shares_by_day


def calculate_commissions_by_day(df: DataFrame):
    """Calculates the commissions charged by day.
    """
    df_by_day = {day: group for day, group in df.groupby('Date')}  # Convert the dataframe to a dictionary. Key: day, value: rows

    commissions_by_day = {}

    for day, rows in df_by_day.items():
        # Create an entry in the dictionary for each day.
        commissions_by_day[day] = 0

        # Get the unique symbols for the day.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # DataFrame filtered by Symbol.

            # Calculate commissions by summing per row.
            commissions = symbol_row[['Comm', 'SEC', 'TAF', 'NSCC', 'CAT']].sum().sum()
            commissions_by_day[day] += commissions

    return commissions_by_day


def calculate_ecn_fees_by_day(df: DataFrame):
    """Calculates the Ecn Fees earned or lost by day.
    """
    df_by_day = {day: group for day, group in df.groupby('Date')}  # Convert the dataframe to a dictionary. Key: day, value: rows

    ecn_fees_by_day = {}

    for day, rows in df_by_day.items():
        # Create an entry in the dictionary for each day.
        ecn_fees_by_day[day] = 0

        # Get the unique symbols for the day.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # DataFrame filtered by Symbol.

            # Calculate ECN fees by summing per row.
            ecn_fees = symbol_row['Ecn Fee'].sum()

            ecn_fees_by_day[day] += ecn_fees

    return ecn_fees_by_day


def get_won_lost_trades_by_day(df: DataFrame):
    """Obtains the number of won and lost trades by day.
    """
    trade_history = get_trades_by_date(df)
    result = {}

    for date, (asset, trade_result) in trade_history.items():
        # Extract the date (year, month, day)
        day = date.date()

        # If the date is not in the dictionary, initialize it with an empty dictionary
        if day not in result:
            result[day] = {'winners': 0, 'losers': 0}

        # Count winners and losers
        if trade_result > 0:
            result[day]['winners'] += 1
        else:
            result[day]['losers'] += 1

    return result
