from datetime import datetime, timedelta

def get_date_range(period):
    end_date = datetime.now()
    if period == 'day':
        start_date = end_date - timedelta(days=1)
    elif period == 'week':
        start_date = end_date - timedelta(weeks=1)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    else:
        raise ValueError("Noto'g'ri davr: 'day', 'week' yoki 'month' dan birini tanlang.")
    return start_date, end_date
