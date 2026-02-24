from datetime import datetime, timedelta

# TASK1 - Subtract five days from current date
today = datetime.now()
five_days_ago = today - timedelta(days=5)
print(five_days_ago.strftime("%Y-%m-%d"))


# TASK2 - Print yesterday, today, tomorrow
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print("Yesterday:", yesterday.strftime("%Y-%m-%d"))
print("Today:", today.strftime("%Y-%m-%d"))
print("Tomorrow:", tomorrow.strftime("%Y-%m-%d"))


# TASK3 - Drop microseconds from datetime
now_with_microseconds = datetime.now()
now_without_microseconds = now_with_microseconds.replace(microsecond=0)
print(now_without_microseconds)


# TASK4 - Calculate two date difference in seconds
date1 = datetime(2023, 1, 1)
date2 = datetime(2023, 12, 31)
diff = date2 - date1
print(int(diff.total_seconds()))
