import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

def get_all_trades(limit: int = 100, ticker: str = None, 
                  min_ts: int = None, max_ts: int = None):
    """
    Get all trades with pagination support.
    
    Args:
        limit: Maximum trades per request
        ticker: Ticker filter
        min_ts: Minimum timestamp filter
        max_ts: Maximum timestamp filter
        
    Returns:
        List of all trades
    """
    from kalshi.rest.market import Market
    
    market = Market()
    all_trades = []
    cursor = None
    while True:
        resp = market.GetTrades(limit=limit, cursor=cursor, ticker=ticker,
                               min_ts=min_ts, max_ts=max_ts)
        all_trades.extend(resp.get("trades", []))
        cursor = resp.get("cursor")
        if not cursor:
            break
    return all_trades



def get_all_orders(limit: int = 100, status: str = None, 
                  ticker: str = None, event_ticker: str = None):
    """
    Get all orders with pagination support.
    
    Args:
        limit: Maximum orders per request
        status: Order status filter
        ticker: Ticker filter
        event_ticker: Event ticker filter
        
    Returns:
        List of all orders
    """
    from kalshi_api.rest import portfolio
    
    all_orders = []
    cursor = None
    while True:
        resp = portfolio.GetOrders(limit=limit, cursor=cursor, status=status, 
                                 ticker=ticker, event_ticker=event_ticker)
        all_orders.extend(resp.get("orders", []))
        cursor = resp.get("cursor")
        if not cursor:
            break
    return all_orders


def cancel_all_resting_orders(ticker: str = None, event_ticker: str = None) -> Dict:
    """
    Cancel all resting (open) orders.
    
    Args:
        ticker: Optional ticker filter
        event_ticker: Optional event ticker filter
        
    Returns:
        Dictionary with cancellation results
    """
    from kalshi_api.rest import portfolio
    
    to_cancel = get_all_orders(status="resting", ticker=ticker, event_ticker=event_ticker)
    results = []
    for o in to_cancel:
        oid = o.get("order_id")
        try:
            resp = portfolio.CancelOrder(order_id=oid)
            results.append({"order_id": oid, "ok": True, "response": resp})
        except Exception as e:
            results.append({"order_id": oid, "ok": False, "error": str(e)})
    return {"requested": len(to_cancel), "cancelled": sum(r["ok"] for r in results), "results": results} 


def plot_trades(trades_df: pd.DataFrame, 
                start_timestamp: Optional[datetime] = None,
                duration_hours: Optional[float] = None,
                title: str = "Trade History",
                figsize: Tuple[int, int] = (12, 8)) -> None:
    """
    Plot trades over time with size-based coloring and taker direction arrows.
    
    Args:
        trades_df: DataFrame containing trade data with columns:
                   trade_id, ticker, count, created_time, yes_price, no_price, taker_side
        start_timestamp: Optional start time for filtering trades
        duration_hours: Optional duration in hours from start_timestamp
        title: Plot title
        figsize: Figure size as (width, height)
    """
    if len(trades_df) == 0:
        print("No trade data to plot")
        return
    
    # Create a copy to avoid modifying original data
    df = trades_df.copy()
    
    # Ensure created_time is datetime
    if 'created_time' not in df.columns:
        raise ValueError("DataFrame must contain 'created_time' column")
    
    if not pd.api.types.is_datetime64_any_dtype(df['created_time']):
        df['created_time'] = pd.to_datetime(df['created_time'])
    
    # Filter by time range if specified
    if start_timestamp is not None:
        # Convert start_timestamp to timezone-aware if needed to match created_time
        if df['created_time'].dt.tz is not None and start_timestamp.tzinfo is None:
            start_timestamp = pd.to_datetime(start_timestamp, utc=True)
        elif df['created_time'].dt.tz is None and start_timestamp.tzinfo is not None:
            start_timestamp = start_timestamp.replace(tzinfo=None)
        
        df = df[df['created_time'] >= start_timestamp]
        if duration_hours is not None:
            end_timestamp = start_timestamp + timedelta(hours=duration_hours)
            df = df[df['created_time'] <= end_timestamp]
    
    if len(df) == 0:
        print(f"No trades found in specified time range for {title}")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Normalize trade sizes for color mapping
    trade_sizes = df['count']
    norm = Normalize(vmin=trade_sizes.min(), vmax=trade_sizes.max())
    
    # Create scatter plot with size-based coloring
    scatter = ax.scatter(df['created_time'], df['yes_price'], 
                        c=df['count'], cmap='plasma', 
                        s=100, alpha=0.8, norm=norm, edgecolors='white', linewidth=0.5)
    
    # Add colorbar for trade size
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Trade Size (contracts)', rotation=270, labelpad=20)
    
    # Add arrows for taker direction - positioned to the side of points
    time_range = (df['created_time'].max() - df['created_time'].min()).total_seconds()
    arrow_offset_x = pd.Timedelta(seconds=time_range * 0.01)  # 1% of time range
    arrow_size = 0.015 * (df['yes_price'].max() - df['yes_price'].min())
    
    # Calculate summary statistics
    total_volume = df['count'].sum()
    weighted_avg_price = (df['yes_price'] * df['count']).sum() / df['count'].sum()
    
    for _, trade in df.iterrows():
        x = trade['created_time']
        y = trade['yes_price']
        
        if trade['taker_side'] == 'yes':
            # Up arrow for yes taker - positioned to the right
            arrow_x = x + arrow_offset_x
            ax.annotate('', xy=(arrow_x, y + arrow_size), xytext=(arrow_x, y - arrow_size),
                       arrowprops=dict(arrowstyle='->', color='green', lw=2, alpha=0.9))
        else:
            # Down arrow for no taker - positioned to the left
            arrow_x = x - arrow_offset_x
            ax.annotate('', xy=(arrow_x, y - arrow_size), xytext=(arrow_x, y + arrow_size),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2, alpha=0.9))
    
    # Format plot
    ax.set_ylabel('Yes Price (cents)')
    ax.set_xlabel('Time')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis for better time display with adaptive resolution
    time_span_hours = (df['created_time'].max() - df['created_time'].min()).total_seconds() / 3600
    
    # Set x-axis limits to show full time window if specified
    if start_timestamp is not None:
        if duration_hours is not None:
            end_timestamp = start_timestamp + timedelta(hours=duration_hours)
            ax.set_xlim(start_timestamp, end_timestamp)
            # Use the specified duration for grid calculation instead of actual data span
            time_span_hours = duration_hours
        else:
            ax.set_xlim(start_timestamp, df['created_time'].max())
    
    if time_span_hours <= 2:  # For windows up to 2 hours
        # Major gridlines every 5 minutes, minor ticks every minute
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.grid(True, which='major', alpha=0.5)
        ax.grid(True, which='minor', alpha=0.2)
    elif time_span_hours <= 6:  # For windows up to 6 hours
        # Major gridlines every 15 minutes, minor ticks every 5 minutes
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.grid(True, which='major', alpha=0.5)
        ax.grid(True, which='minor', alpha=0.2)
    elif time_span_hours <= 24:  # For windows up to 24 hours
        # Major gridlines every hour, minor ticks every 15 minutes
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.grid(True, which='major', alpha=0.5)
        ax.grid(True, which='minor', alpha=0.2)
    else:  # For longer windows
        # Major gridlines every 6 hours, minor ticks every hour
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.grid(True, which='major', alpha=0.5)
        ax.grid(True, which='minor', alpha=0.2)
    
    plt.xticks(rotation=45)
    
    # Add summary statistics below the plot
    stats_text = f'Total Volume: {total_volume:,} contracts    |    Weighted Avg Price: {weighted_avg_price:.1f}¢'
    plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=11, 
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Make room for statistics
    plt.show()


def calculate_vwap(trades_df: pd.DataFrame, price_col: str = 'yes_price', 
                   volume_col: str = 'count') -> float:
    """
    Calculate Volume Weighted Average Price (VWAP) from trade data.
    
    Args:
        trades_df: DataFrame containing trade data
        price_col: Column name containing prices
        volume_col: Column name containing volumes
        
    Returns:
        VWAP as float
    """
    if len(trades_df) == 0:
        return 0.0
    
    total_volume = trades_df[volume_col].sum()
    if total_volume == 0:
        return 0.0
    
    volume_weighted_prices = (trades_df[price_col] * trades_df[volume_col]).sum()
    return volume_weighted_prices / total_volume


def calculate_volume_stats(trades_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate taker volume statistics for yes vs no sides.
    
    Args:
        trades_df: DataFrame containing trade data with columns:
                   taker_side, count, yes_price
                   
    Returns:
        Dictionary containing volume statistics
    """
    if len(trades_df) == 0:
        return {
            'yes_taker_volume': 0,
            'no_taker_volume': 0,
            'total_volume': 0,
            'yes_taker_percentage': 0,
            'no_taker_percentage': 0,
            'yes_taker_dollar_volume': 0,
            'no_taker_dollar_volume': 0,
            'total_dollar_volume': 0,
            'yes_dollar_percentage': 0,
            'no_dollar_percentage': 0
        }
    
    # Calculate taker volume on yes vs no side
    yes_taker_volume = trades_df[trades_df['taker_side'] == 'yes']['count'].sum()
    no_taker_volume = trades_df[trades_df['taker_side'] == 'no']['count'].sum()
    total_volume = yes_taker_volume + no_taker_volume
    
    # Calculate dollar volume for each side
    yes_taker_dollar_volume = (trades_df[trades_df['taker_side'] == 'yes']['yes_price'] * 
                              trades_df[trades_df['taker_side'] == 'yes']['count']).sum() / 100
    # For no takers, they pay the no_price which is (100 - yes_price)
    no_taker_dollar_volume = ((100 - trades_df[trades_df['taker_side'] == 'no']['yes_price']) * 
                             trades_df[trades_df['taker_side'] == 'no']['count']).sum() / 100
    total_dollar_volume = yes_taker_dollar_volume + no_taker_dollar_volume
    
    return {
        'yes_taker_volume': yes_taker_volume,
        'no_taker_volume': no_taker_volume,
        'total_volume': total_volume,
        'yes_taker_percentage': yes_taker_volume/total_volume*100 if total_volume > 0 else 0,
        'no_taker_percentage': no_taker_volume/total_volume*100 if total_volume > 0 else 0,
        'yes_taker_dollar_volume': yes_taker_dollar_volume,
        'no_taker_dollar_volume': no_taker_dollar_volume,
        'total_dollar_volume': total_dollar_volume,
        'yes_dollar_percentage': yes_taker_dollar_volume/total_dollar_volume*100 if total_dollar_volume > 0 else 0,
        'no_dollar_percentage': no_taker_dollar_volume/total_dollar_volume*100 if total_dollar_volume > 0 else 0
    }