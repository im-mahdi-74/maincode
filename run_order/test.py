from datetime import datetime, timezone
import pytz

utc_time = datetime.fromtimestamp(1741714497.4965239, tz=timezone.utc)

# تبدیل به timezone ایران
iran_timezone = pytz.timezone('Asia/Tehran')
iran_time = utc_time.astimezone(iran_timezone)

print(iran_time)