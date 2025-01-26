from pandas import DataFrame
from calculations.row_calculations import calculate_commissions_per_row, get_individual_trades_per_day


def calculate_gross_pnl_total(df: DataFrame):
    """Calculates the total PNL before commissions and ECN fees.
    """
    accumulated_purchase_money = 0
    accumulated_sale_money = 0
    for _, row in df.iterrows():
      if row['B/S'] == 'S' or row['B/S'] == 'T':
        accumulated_sale_money += row['Qty'] * row['Price']
      else:
        accumulated_purchase_money -= row['Qty'] * row['Price']

    return accumulated_purchase_money + accumulated_sale_money


def calculate_net_pnl_total(df: DataFrame):
  """Calculates the total PNL after applying commissions and ECN fees.
  """
  accumulated_purchase_money = 0
  accumulated_sale_money = 0
  accumulated_commissions = 0
  accumulated_ecn = 0
  for _, row in df.iterrows():
    commissions, ecn_fees = calculate_commissions_per_row(row)
    accumulated_commissions += commissions
    accumulated_ecn += ecn_fees
    if row['B/S'] == 'S' or row['B/S'] == 'T':
      accumulated_sale_money += row['Qty'] * row['Price']
    else:
      accumulated_purchase_money -= row['Qty'] * row['Price']

  return (accumulated_purchase_money + accumulated_sale_money) - (accumulated_ecn + accumulated_commissions)


def calculate_total_commissions(df: DataFrame):
  """Calculates the total commissions.
  """
  accumulated_commissions = 0
  for _, row in df.iterrows():
    commissions, ecn_fees = calculate_commissions_per_row(row)
    accumulated_commissions += commissions
  return accumulated_commissions


def calculate_total_ecn_fees(df: DataFrame):
  """Calculates the total ECN fees. If negative, it means money gained.
  """
  accumulated_ecn = 0
  for _, row in df.iterrows():
    commissions, ecn_fees = calculate_commissions_per_row(row)
    accumulated_ecn += ecn_fees
  return accumulated_ecn


def calculate_total_shares(df: DataFrame):
    """Calculates the total number of shares bought, sold, and shorted based on the 'B/S' column (Buy, Sell, Short).
    """
    # Initialize the dictionary.
    total_shares = {'Buy': 0, 'Sell': 0, 'Short': 0}

    # Iterate over the rows of the DataFrame.
    for _, row in df.iterrows():
        # Add to the corresponding key based on the 'B/S' value.
        if row['B/S'] == 'B':
            total_shares['Buy'] += row['Qty']
        elif row['B/S'] == 'S':
            total_shares['Sell'] += row['Qty']
        elif row['B/S'] == 'T':
            total_shares['Short'] += row['Qty']

    # Check that the number of shares matches.
    if total_shares['Buy'] != total_shares['Sell'] + total_shares['Short']:
      raise ValueError(f"The total 'Buy' ({total_shares['Buy']}) does not match the sum of 'Sell' ({total_shares['Sell']}) and 'Short' ({total_shares['Short']}).")

    return total_shares


def calculate_winning_trades(df: DataFrame):
  """Calculates the quantity of winning result trades.
  """
  accumulated_money = {}
  share_count = {}
  winning_trades = 0
  losing_trades = 0

  for _, row in df.iterrows():
    symbol = row['Symbol']
    if symbol not in accumulated_money:
      accumulated_money[symbol] = 0
      share_count[symbol] = 0

    if row['B/S'] == 'B':
     share_count[symbol] += row['Qty']
     accumulated_money[symbol] -= row['Qty'] * row['Price']
    else:
      share_count[symbol] -= row['Qty']
      accumulated_money[symbol] += row['Qty'] * row['Price']

    commissions, ecn_fees = calculate_commissions_per_row(row)
    accumulated_money[symbol] -= ecn_fees + commissions

    if share_count[symbol] == 0:
      if accumulated_money[symbol] > 0:
        winning_trades += 1
      else:
        losing_trades += 1

      # Reset values for the symbol
      accumulated_money[symbol] = 0

  return winning_trades


def calculate_losing_trades(df: DataFrame):
  """Calculates the quantity of losing result trades.
  """
  accumulated_money = {}
  share_count = {}
  winning_trades = 0
  losing_trades = 0

  for _, row in df.iterrows():
    symbol = row['Symbol']
    if symbol not in accumulated_money:
      accumulated_money[symbol] = 0
      share_count[symbol] = 0

    if row['B/S'] == 'B':
      share_count[symbol] += row['Qty']
      accumulated_money[symbol] -= row['Qty'] * row['Price']
    else:
      share_count[symbol] -= row['Qty']
      accumulated_money[symbol] += row['Qty'] * row['Price']

    commissions, ecn_fees = calculate_commissions_per_row(row)
    accumulated_money[symbol] -= ecn_fees + commissions

    if share_count[symbol] == 0:
      if accumulated_money[symbol] > 0:
        winning_trades += 1
      else:
        losing_trades += 1

      # Reset values for the symbol
      accumulated_money[symbol] = 0

  return losing_trades


def calculate_avg_winning_and_losing_trades(df: DataFrame):
  """Calculates the average of winning and losing trades.
  """
  trades_dict = get_individual_trades_per_day(df)
  winning_trades = []
  losing_trades = []

  for date, trades in trades_dict.items():
      for trade in trades:
          pnl = trade['PnL']
          if pnl > 0:
              winning_trades.append(pnl)
          elif pnl < 0:
              losing_trades.append(pnl)

  avg_winners = sum(winning_trades) / len(winning_trades) if winning_trades else 0
  avg_losers = sum(losing_trades) / len(losing_trades) if losing_trades else 0

  return {
      'avg_winning_trades': avg_winners,
      'avg_losing_trades': avg_losers
  }


def calculate_filtered_avg_winning_and_losing_trades(df: DataFrame):
  """Calculates the average of winning and losing trades removing trades between -1 and 1 pnl.
  """
  trades_dict = get_individual_trades_per_day(df)
  winning_trades = []
  losing_trades = []

  for date, trades in trades_dict.items():
      for trade in trades:
          pnl = trade['PnL']
          if pnl > 1:
              winning_trades.append(pnl)
          elif pnl < -1:
              losing_trades.append(pnl)

  avg_winners = sum(winning_trades) / len(winning_trades) if winning_trades else 0
  avg_losers = sum(losing_trades) / len(losing_trades) if losing_trades else 0

  return {
      'avg_winning_trades': avg_winners,
      'avg_losing_trades': avg_losers
  }


def calculate_accuracy_percentage(df: DataFrame):
  """Calculates the percentage of successfull trades.
  """
  winning_trades = calculate_winning_trades(df)
  losing_trades = calculate_losing_trades(df)
  total_trades = winning_trades + losing_trades

  accuracy_percentage = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
  return accuracy_percentage


def calculate_profit_factor(df: DataFrame):
  """Calculates the profit factor.
  """
  trades_dict = get_individual_trades_per_day(df)
  winning_trades = []
  losing_trades = []

  for date, trades in trades_dict.items():
      for trade in trades:
          pnl = trade['PnL']
          if pnl > 0:
              winning_trades.append(pnl)
          elif pnl < 0:
              losing_trades.append(pnl)

  sum_winning_trades = sum(winning_trades) if winning_trades else 0
  sum_losing_trades = sum(losing_trades) if losing_trades else 0

  if sum_losing_trades == 0:
    return float('inf')  # Avoid division by zero

  return sum_winning_trades / abs(sum_losing_trades)


def calculate_filtered_profit_factor(df: DataFrame):
  """Calculates the profit factor removing trades between -1 and 1.
  """
  trades_dict = get_individual_trades_per_day(df)
  winning_trades = []
  losing_trades = []

  for date, trades in trades_dict.items():
      for trade in trades:
          pnl = trade['PnL']
          if pnl > 0 and pnl > 1:
              winning_trades.append(pnl)
          elif pnl < 0 and pnl < -1:
              losing_trades.append(pnl)

  sum_winning_trades = sum(winning_trades) if winning_trades else 0
  sum_losing_trades = sum(losing_trades) if losing_trades else 0

  if sum_losing_trades == 0:
    return float('inf')  # Avoid division by zero

  return sum_winning_trades / abs(sum_losing_trades)
