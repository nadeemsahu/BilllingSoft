def format_currency(amount: float) -> str:
    """Format a float into a currency string."""
    return f"₹{amount:,.2f}"

def format_date(date_string: str) -> str:
    """Format a database datetime string to a more readable format."""
    if not date_string:
        return ""
    try:
        from datetime import datetime
        dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y - %I:%M %p")
    except ValueError:
        return date_string
