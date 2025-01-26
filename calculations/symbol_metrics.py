from pandas import DataFrame
from calculations.row_calculations import get_trades_by_symbol_and_date


def calculate_gross_pnl_by_symbol(df: DataFrame):
    """Calculates the gross PnL by symbol, adjusting the sign based on the 'B/S' column.
    """
    # Get the entire list of unique symbols.
    symbol_list = df['Symbol'].drop_duplicates().tolist()

    # Initialize the dictionary with values set to 0.
    gross_pnl_by_symbol = {symbol: 0 for symbol in symbol_list}

    # Convert the DataFrame into a dictionary. Key: day, Value: DataFrame rows.
    df_by_day = {day: group for day, group in df.groupby('Date')}

    for day, rows in df_by_day.items():
        # Get the unique symbols for the day being processed.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # DataFrame with rows filtered by Symbol.

            # Calculate the gross PnL, ignoring commissions.
            calculation = ((symbol_row['Price'] * symbol_row['Qty']) * symbol_row['B/S'].apply(lambda x: -1 if x in ['B'] else 1)).sum()

            # Add the result to the dictionary
            gross_pnl_by_symbol[symbol] += calculation

    return gross_pnl_by_symbol


def calculate_net_pnl_by_symbol(df: DataFrame):
    """Calculates the net PnL by symbol.
    """
    # Get the entire list of unique symbols.
    symbol_list = df['Symbol'].drop_duplicates().tolist()

    # Initialize the dictionary with values set to 0.
    net_pnl_by_symbol = {symbol: 0 for symbol in symbol_list}

    # Convert the DataFrame into a dictionary. Key: day, Value: DataFrame rows.
    df_by_day = {day: group for day, group in df.groupby('Date')}

    for day, rows in df_by_day.items():
        # Get the unique symbols for the day being processed.
        symbols_for_day = rows['Symbol'].drop_duplicates().tolist()

        for symbol in symbols_for_day:
            symbol_row = rows[rows['Symbol'] == symbol]  # DataFrame with rows filtered by Symbol.

            # Calculate the gross PnL, ignoring commissions.
            calculation = ((symbol_row['Price'] * symbol_row['Qty']) * symbol_row['B/S'].apply(lambda x: -1 if x in ['B'] else 1)).sum()

            # Calculate commissions and ECN fees by summing the commissions per row
            commissions = symbol_row[['Comm', 'SEC', 'TAF', 'NSCC', 'CAT']].sum().sum()
            ecn_fees = symbol_row['Ecn Fee'].sum()

            # Adjust the PnL calculation with the commissions and ECN fees
            calculation = calculation - commissions + ecn_fees * -1

            # Add the result to the dictionary
            net_pnl_by_symbol[symbol] += calculation

    return net_pnl_by_symbol


def get_won_lost_trades_by_symbol(df: DataFrame):
    """Generates a dictionary with the number of won and lost trades by symbol.
    """
    trade_history = get_trades_by_symbol_and_date(df)

    symbol_trade_result = {}
    for symbol, dates_pnls in trade_history.items():
        for date, pnl in dates_pnls.items():

            # Initialize the counter for the symbol if it doesn't exist
            if symbol not in symbol_trade_result:
                symbol_trade_result[symbol] = {'won': 0, 'lost': 0}

            # Increment the counter for won or lost trades based on the PnL
            #TODO: Filter trades between -1 and 1.
            if pnl > 0:
                symbol_trade_result[symbol]['won'] += 1
            else:
                symbol_trade_result[symbol]['lost'] += 1

    return symbol_trade_result
