from pandas import DataFrame, Series

def calculate_commissions_per_row(row: Series):
    """Calculates the commissions and fees of a trade.

    All commission-related values are summed up in 'commissions', while ecn_fees are handled separately because they can either add or subtract.

    :param row: Row from which commissions are extracted.
    :return commissions, ecn_fee: float, float representing the commissions and ecn fees earned or lost.
    """
    # Sum the commissions from the relevant columns
    commissions = sum(row[col] for col in ['Comm', 'SEC', 'TAF', 'NSCC', 'CAT'])

    # Get the value of 'Ecn Fee'
    ecn_fee = row['Ecn Fee']

    return commissions, ecn_fee


def get_trades_by_symbol_and_date(df: DataFrame):
    """Generates a dictionary by symbol, and for each trading day, gets the PnL at the end of the day (with commissions applied).
    """
    current_trade_value = {}
    accumulated_money_per_day = {}
    share_count = {}
    winning_trades = 0
    losing_trades = 0
    trades_pnl_per_day = {}

    for _, row in df.iterrows():
        symbol = row['Symbol']
        date = row['Date']

        # Initialize the dictionaries for the symbol and date if they don't exist
        if symbol not in current_trade_value:
            current_trade_value[symbol] = 0
            accumulated_money_per_day[symbol] = 0
            share_count[symbol] = 0
        if symbol not in trades_pnl_per_day:
            trades_pnl_per_day[symbol] = {}
        if date not in trades_pnl_per_day[symbol]:
            trades_pnl_per_day[symbol][date] = 0

        # Update the share count and current_trade_value based on the trade
        if row['B/S'] == 'B':
            share_count[symbol] += row['Qty']
            current_trade_value[symbol] -= row['Qty'] * row['Price']
        else:
            share_count[symbol] -= row['Qty']
            current_trade_value[symbol] += row['Qty'] * row['Price']

        # Calculate commissions and subtract them
        commissions, ecn_fees = calculate_commissions_per_row(row)
        current_trade_value[symbol] -= (ecn_fees + commissions)

        # Update the accumulated daily value
        accumulated_money_per_day[symbol] += current_trade_value[symbol]

        # If the position is closed, evaluate the result of the trade
        if share_count[symbol] == 0:
            if current_trade_value[symbol] > 0:
                trades_pnl_per_day[symbol][date] += current_trade_value[symbol]
                winning_trades += 1
            else:
                trades_pnl_per_day[symbol][date] += current_trade_value[symbol]
                losing_trades += 1

            # Reset current_trade_value but keep the accumulated daily value
            current_trade_value[symbol] = 0

    return trades_pnl_per_day


def get_trades_by_symbol_date_and_time(df: DataFrame):
    """Generates a dictionary by symbol, and for each trading day and time, gets the PnL of each trade (with commissions applied).
    """
    current_trade_value = {}
    accumulated_money_per_day = {}
    share_count = {}
    winning_trades = 0
    losing_trades = 0
    trades_pnl_per_datetime = {}

    for _, row in df.iterrows():
        symbol = row['Symbol']
        date_time = row['Date/Time']  # We use 'Date/Time' instead of 'Date'

        # Initialize the dictionaries for the symbol if they don't exist
        if symbol not in current_trade_value:
            current_trade_value[symbol] = 0
            accumulated_money_per_day[symbol] = 0
            share_count[symbol] = 0
        if symbol not in trades_pnl_per_datetime:
            trades_pnl_per_datetime[symbol] = {}

        # Update the share count and current_trade_value based on the trade
        if row['B/S'] == 'B':
            share_count[symbol] += row['Qty']
            current_trade_value[symbol] -= row['Qty'] * row['Price']
        else:
            share_count[symbol] -= row['Qty']
            current_trade_value[symbol] += row['Qty'] * row['Price']

        # Calculate commissions and subtract them
        commissions, ecn_fees = calculate_commissions_per_row(row)
        current_trade_value[symbol] -= (ecn_fees + commissions)

        # Update the accumulated daily value
        accumulated_money_per_day[symbol] += current_trade_value[symbol]

        # If the position is closed, evaluate the result of the trade and log the PnL
        if share_count[symbol] == 0:
            if current_trade_value[symbol] > 0:
                trades_pnl_per_datetime[symbol][date_time] = current_trade_value[symbol]
                winning_trades += 1
            else:
                trades_pnl_per_datetime[symbol][date_time] = current_trade_value[symbol]
                losing_trades += 1

            # Reset current_trade_value but keep the accumulated daily value
            current_trade_value[symbol] = 0

    return trades_pnl_per_datetime

def get_trades_by_date(df: DataFrame):
    """Generates a dictionary sorted by datetime, where the key is the datetime and the value is a tuple (symbol, pnl).
    """
    current_trade_value = {}
    accumulated_money_per_day = {}
    share_count = {}
    winning_trades = 0
    losing_trades = 0
    trades_pnl_per_datetime = {}

    for _, row in df.iterrows():
        symbol = row['Symbol']
        date_time = row['Date/Time']  # We use 'Date/Time' instead of 'Date'

        # Initialize the dictionaries for the symbol if they don't exist
        if symbol not in current_trade_value:
            current_trade_value[symbol] = 0
            accumulated_money_per_day[symbol] = 0
            share_count[symbol] = 0

        # Update the share count and current_trade_value based on the trade
        if row['B/S'] == 'B':
            share_count[symbol] += row['Qty']
            current_trade_value[symbol] -= row['Qty'] * row['Price']
        else:
            share_count[symbol] -= row['Qty']
            current_trade_value[symbol] += row['Qty'] * row['Price']

        # Calculate commissions and subtract them
        commissions, ecn_fees = calculate_commissions_per_row(row)
        current_trade_value[symbol] -= (ecn_fees + commissions)

        # Update the accumulated daily value
        accumulated_money_per_day[symbol] += current_trade_value[symbol]

        # If the position is closed, evaluate the result of the trade and log the PnL
        if share_count[symbol] == 0:
            if date_time not in trades_pnl_per_datetime:
                trades_pnl_per_datetime[date_time] = (symbol, current_trade_value[symbol])

            if current_trade_value[symbol] > 0:
                winning_trades += 1
            else:
                losing_trades += 1

            # Reset current_trade_value but keep the accumulated daily value
            current_trade_value[symbol] = 0

    return trades_pnl_per_datetime


def get_individual_trades_per_day(df: DataFrame):
    """Generates a dictionary where each key is a date, and its value is a list of trades made on that day.

    Each trade includes the symbol and the individual trade PnL.
    """
    accumulated_money = {}
    share_count = {}
    trades_per_day = {}

    for _, row in df.iterrows():
        symbol = row['Symbol']
        date = row['Date']

        # Ensure the dictionary by date is initialized
        if date not in trades_per_day:
            trades_per_day[date] = []
        if symbol not in accumulated_money:
            accumulated_money[symbol] = 0
            share_count[symbol] = 0

        # Update share count and accumulated money
        if row['B/S'] == 'B':  # Buy
            share_count[symbol] += row['Qty']
            accumulated_money[symbol] -= row['Qty'] * row['Price']
        else:  # Sell
            share_count[symbol] -= row['Qty']
            accumulated_money[symbol] += row['Qty'] * row['Price']

        # Subtract commissions and ECN fees
        commissions, ecn_fees = calculate_commissions_per_row(row)
        accumulated_money[symbol] -= (commissions + ecn_fees)

        # If the share count reaches 0, close the trade and store it
        if share_count[symbol] == 0:
            trade_pnl = accumulated_money[symbol]
            trade_info = {'Symbol': symbol, 'PnL': trade_pnl}

            # Store the trade in the list for the corresponding date
            trades_per_day[date].append(trade_info)

            # Reset the accumulated money for the symbol
            accumulated_money[symbol] = 0

    return trades_per_day
