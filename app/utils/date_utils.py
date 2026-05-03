from datetime import datetime, timedelta
import calendar
import pytz

class DateUtils:
    @staticmethod
    def format_date(date_obj, format_string='%Y-%m-%d'):
        """Format date object"""
        if not date_obj:
            return ""
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
                except ValueError:
                    return date_obj
        
        return date_obj.strftime(format_string)
    
    @staticmethod
    def format_datetime(datetime_obj, format_string='%Y-%m-%d %H:%M:%S'):
        """Format datetime object"""
        if not datetime_obj:
            return ""
        
        if isinstance(datetime_obj, str):
            try:
                datetime_obj = datetime.strptime(datetime_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return datetime_obj
        
        return datetime_obj.strftime(format_string)
    
    @staticmethod
    def format_time(time_obj, format_string='%H:%M:%S'):
        """Format time object"""
        if not time_obj:
            return ""
        
        if isinstance(time_obj, str):
            try:
                time_obj = datetime.strptime(time_obj, '%H:%M:%S')
            except ValueError:
                return time_obj
        
        return time_obj.strftime(format_string)
    
    @staticmethod
    def parse_date(date_string, format_string='%Y-%m-%d'):
        """Parse date string"""
        if not date_string:
            return None
        
        try:
            return datetime.strptime(date_string, format_string)
        except ValueError:
            return None
    
    @staticmethod
    def parse_datetime(datetime_string, format_string='%Y-%m-%d %H:%M:%S'):
        """Parse datetime string"""
        if not datetime_string:
            return None
        
        try:
            return datetime.strptime(datetime_string, format_string)
        except ValueError:
            return None
    
    @staticmethod
    def parse_time(time_string, format_string='%H:%M:%S'):
        """Parse time string"""
        if not time_string:
            return None
        
        try:
            return datetime.strptime(time_string, format_string)
        except ValueError:
            return None
    
    @staticmethod
    def to_iso_string(date_obj):
        """Convert date to ISO string"""
        if not date_obj:
            return ""
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return date_obj
        
        return date_obj.isoformat()
    
    @staticmethod
    def from_iso_string(iso_string):
        """Parse ISO string to datetime"""
        if not iso_string:
            return None
        
        try:
            return datetime.fromisoformat(iso_string)
        except ValueError:
            return None
    
    @staticmethod
    def get_relative_time(date_obj):
        """Get relative time string"""
        if not date_obj:
            return ""
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return date_obj
        
        now = datetime.utcnow()
        diff = now - date_obj
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "just now"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
    
    @staticmethod
    def get_time_remaining(date_obj):
        """Get time remaining until date"""
        if not date_obj:
            return ""
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return date_obj
        
        now = datetime.utcnow()
        diff = date_obj - now
        
        if diff.total_seconds() < 0:
            return "overdue"
        
        if diff.days == 0:
            if diff.seconds < 60:
                return f"{diff.seconds} second{'s' if diff.seconds != 1 else ''}"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''}"
        elif diff.days == 1:
            return "1 day"
        elif diff.days < 7:
            return f"{diff.days} days"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''}"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''}"
        else:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''}"
    
    @staticmethod
    def is_today(date_obj):
        """Check if date is today"""
        if not date_obj:
            return False
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        
        today = datetime.utcnow().date()
        return date_obj.date() == today
    
    @staticmethod
    def is_yesterday(date_obj):
        """Check if date is yesterday"""
        if not date_obj:
            return False
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        return date_obj.date() == yesterday
    
    @staticmethod
    def is_tomorrow(date_obj):
        """Check if date is tomorrow"""
        if not date_obj:
            return False
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        return date_obj.date() == tomorrow
    
    @staticmethod
    def is_this_week(date_obj):
        """Check if date is this week"""
        if not date_obj:
            return False
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        return week_start <= date_obj.date() <= week_end
    
    @staticmethod
    def is_this_month(date_obj):
        """Check if date is this month"""
        if not date_obj:
            return False
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        
        today = datetime.utcnow().date()
        return date_obj.year == today.year and date_obj.month == today.month
    
    @staticmethod
    def is_this_year(date_obj):
        """Check if date is this year"""
        if not date_obj:
            return False
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        
        today = datetime.utcnow().date()
        return date_obj.year == today.year
    
    @staticmethod
    def get_start_of_day(date_obj):
        """Get start of day"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_end_of_day(date_obj):
        """Get end of day"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def get_start_of_week(date_obj):
        """Get start of week (Monday)"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_end_of_week(date_obj):
        """Get end of week (Sunday)"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        end_of_week = date_obj + timedelta(days=(6 - date_obj.weekday()))
        return end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def get_start_of_month(date_obj):
        """Get start of month"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_end_of_month(date_obj):
        """Get end of month"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
        return date_obj.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def add_days(date_obj, days):
        """Add days to date"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj + timedelta(days=days)
    
    @staticmethod
    def subtract_days(date_obj, days):
        """Subtract days from date"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj - timedelta(days=days)
    
    @staticmethod
    def add_hours(date_obj, hours):
        """Add hours to date"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj + timedelta(hours=hours)
    
    @staticmethod
    def subtract_hours(date_obj, hours):
        """Subtract hours from date"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj - timedelta(hours=hours)
    
    @staticmethod
    def get_week_number(date_obj):
        """Get week number of the year"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return date_obj.isocalendar()[1]
    
    @staticmethod
    def get_quarter(date_obj):
        """Get quarter of the year"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        month = date_obj.month
        if month in [1, 2, 3]:
            return 1
        elif month in [4, 5, 6]:
            return 2
        elif month in [7, 8, 9]:
            return 3
        else:
            return 4
    
    @staticmethod
    def get_age(birthdate):
        """Get age from birthdate"""
        if not birthdate:
            return None
        
        if isinstance(birthdate, str):
            try:
                birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
            except ValueError:
                return None
        
        today = datetime.utcnow().date()
        age = today.year - birthdate.year
        
        # Adjust if birthday hasn't occurred yet this year
        if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
            age -= 1
        
        return age
    
    @staticmethod
    def get_days_between(date1, date2):
        """Get days between two dates"""
        if not date1 or not date2:
            return None
        
        if isinstance(date1, str):
            try:
                date1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        if isinstance(date2, str):
            try:
                date2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        return abs((date2 - date1).days)
    
    @staticmethod
    def get_business_days_between(date1, date2):
        """Get business days between two dates"""
        if not date1 or not date2:
            return None
        
        if isinstance(date1, str):
            try:
                date1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        if isinstance(date2, str):
            try:
                date2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        
        if date1 > date2:
            date1, date2 = date2, date1
        
        business_days = 0
        current_date = date1
        
        while current_date <= date2:
            if current_date.weekday() < 5:  # Monday to Friday
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    @staticmethod
    def get_weekday_name(date_obj):
        """Get weekday name"""
        if not date_obj:
            return ""
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return ""
        
        return calendar.day_name[date_obj.weekday()]
    
    @staticmethod
    def get_month_name(date_obj):
        """Get month name"""
        if not date_obj:
            return ""
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return ""
        
        return calendar.month_name[date_obj.month]
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in human readable format"""
        try:
            secs = int(seconds)
            
            if secs < 60:
                return f"{secs}s"
            elif secs < 3600:
                minutes = secs // 60
                remaining_secs = secs % 60
                return f"{minutes}m {remaining_secs}s"
            elif secs < 86400:
                hours = secs // 3600
                remaining_mins = (secs % 3600) // 60
                return f"{hours}h {remaining_mins}m"
            else:
                days = secs // 86400
                remaining_hours = (secs % 86400) // 3600
                return f"{days}d {remaining_hours}h"
        except (ValueError, TypeError):
            return "0s"

# Create instance
date_utils = DateUtils()
