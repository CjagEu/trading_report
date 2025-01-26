from calculations.aggregate_calculations import *
from calculations.symbol_metrics import *
from calculations.per_day_metrics import *
from calculations.row_calculations import *
from trading_report.config import *


df = load_data('my-accounts-from-2025-01-01-executions.xls')
df = clean_data(df)


# Obtain metrics
total_net = calculate_net_pnl_total(df)
total_gross = calculate_gross_pnl_total(df)
#------------------------------------------------------
total_day_net = calculate_net_pnl_by_day(df)
total_day_gross = calculate_gross_pnl_by_day(df)
total_accumulated_per_day_net = calculate_cumulative_net_pnl_by_day(df)
total_accumulated_per_day_gross = calculate_cumulative_gross_pnl_by_day(df)
#------------------------------------------------------
total_symbol_net = calculate_net_pnl_by_symbol(df)
total_symbol_gross = calculate_gross_pnl_by_symbol(df)
#------------------------------------------------------
total_shares = calculate_total_shares(df)
shares_per_day = calculate_shares_by_day(df)
#------------------------------------------------------
total_commissions = calculate_total_commissions(df)
total_ecn_fees = calculate_total_ecn_fees(df)
commissions_per_day = calculate_commissions_by_day(df)
ecn_fees_per_day = calculate_ecn_fees_by_day(df)
#------------------------------------------------------
winning_trades = calculate_winning_trades(df)
losing_trades = calculate_losing_trades(df)
winning_losing_trades_per_symbol = get_won_lost_trades_by_symbol(df)
winning_losing_trades_per_day = get_won_lost_trades_by_day(df)
trades_per_symbol = get_trades_by_symbol_and_date(df)
trades_per_symbol_date_time = get_trades_by_symbol_date_and_time(df)
trades_per_date = get_trades_by_date(df)
individual_trades = get_individual_trades_per_day(df)
#------------------------------------------------------
average_winning_losing_trades = calculate_avg_winning_and_losing_trades(df)
average_winning_losing_trades_filtered = calculate_filtered_avg_winning_and_losing_trades(df)
profit_factor = calculate_profit_factor(df)
profit_factor_filtered = calculate_filtered_profit_factor(df)
accuracy_percentage = calculate_accuracy_percentage(df)


# Print the information
print('Net PnL: ', total_net)
print('Gross PnL: ', total_gross)
#------------------------------------------------------
print('Average winning and losing trades: ', average_winning_losing_trades)
print('Average winning and losing trades filtered: ', average_winning_losing_trades_filtered)
print('Profit factor: ', profit_factor)
print('Profit factor filtered: ', profit_factor_filtered)
print('Accuracy percentage: ', accuracy_percentage)
#------------------------------------------------------
print('Winning trades: ', winning_trades)
print('Losing trades: ', losing_trades)
#------------------------------------------------------
print('Total commissions: ', total_commissions)
print('Total ecn fees: ', total_ecn_fees)
#------------------------------------------------------
print('Total shares: ', total_shares)
#------------------------------------------------------
print('Shares per day: ', shares_per_day)
print('Commissions per day: ', commissions_per_day)
print('Ecn fees per day: ', ecn_fees_per_day)
#------------------------------------------------------
print('Total net per day: ', total_day_net)
print('Total gross per day: ', total_day_gross)
print('Total accumulated net per day: ', total_accumulated_per_day_net)
print('Total accumulated gross per day: ', total_accumulated_per_day_gross)
#------------------------------------------------------
print('Total net per symbol: ', total_symbol_net)
print('Total gross per symbol: ', total_symbol_gross)
#------------------------------------------------------
print('Winning and losing trades per symbol: ', winning_losing_trades_per_symbol)
print('Winning and losing trades per day: ', winning_losing_trades_per_day)
print('Trades per symbol and date: ', trades_per_symbol)
print('Trades per symbol, date and time: ', trades_per_symbol_date_time)
print('Trades per date: ', trades_per_date)
print('Individual trades: ', individual_trades)
#------------------------------------------------------

print('ss')