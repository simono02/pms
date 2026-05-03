import re
import math
from datetime import datetime, timedelta

class Formatters:
    @staticmethod
    def format_currency(amount, currency='USD', locale='en-US'):
        """Format currency amount"""
        try:
            amount_float = float(amount)
            if currency == 'USD':
                return f"${amount_float:,.2f}"
            elif currency == 'EUR':
                return f"€{amount_float:,.2f}"
            elif currency == 'GBP':
                return f"£{amount_float:,.2f}"
            else:
                return f"{amount_float:,.2f} {currency}"
        except (ValueError, TypeError):
            return f"0.00 {currency}"
    
    @staticmethod
    def format_number(number, decimals=2):
        """Format number with specified decimals"""
        try:
            num_float = float(number)
            return f"{num_float:,.{decimals}f}"
        except (ValueError, TypeError):
            return "0"
    
    @staticmethod
    def format_percentage(value, decimals=1):
        """Format as percentage"""
        try:
            value_float = float(value)
            return f"{value_float:.{decimals}f}%"
        except (ValueError, TypeError):
            return "0%"
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human readable format"""
        try:
            size = int(size_bytes)
            if size == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = 0
            while size >= 1024 and i < len(size_names) - 1:
                size /= 1024.0
                i += 1
            
            return f"{size:.1f} {size_names[i]}"
        except (ValueError, TypeError):
            return "0 B"
    
    @staticmethod
    def format_phone_number(phone):
        """Format phone number"""
        if not phone:
            return ""
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone
    
    @staticmethod
    def format_credit_card(card_number):
        """Format credit card number (show last 4 digits)"""
        if not card_number:
            return ""
        
        digits = re.sub(r'\D', '', card_number)
        if len(digits) < 4:
            return ""
        
        # Show only last 4 digits
        last_four = digits[-4:]
        masked_length = len(digits) - 4
        return "*" * masked_length + last_four
    
    @staticmethod
    def format_expiry_date(expiry_date):
        """Format expiry date"""
        if not expiry_date:
            return ""
        
        # Remove any non-digit characters
        digits = re.sub(r'\D', '', expiry_date)
        
        if len(digits) == 4:
            return f"{digits[:2]}/{digits[2:]}"
        else:
            return expiry_date
    
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
    def format_string_case(text, case_type='title'):
        """Format string case"""
        if not text:
            return ""
        
        if case_type == 'title':
            return text.title()
        elif case_type == 'upper':
            return text.upper()
        elif case_type == 'lower':
            return text.lower()
        elif case_type == 'sentence':
            return text.capitalize()
        elif case_type == 'camel':
            parts = text.split()
            return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
        elif case_type == 'pascal':
            parts = text.split()
            return ''.join(word.capitalize() for word in parts)
        elif case_type == 'snake':
            return re.sub(r'\W+', '_', text).lower()
        elif case_type == 'kebab':
            return re.sub(r'\W+', '-', text).lower()
        else:
            return text
    
    @staticmethod
    def truncate_string(text, max_length=50, suffix='...'):
        """Truncate string to specified length"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def slugify(text):
        """Convert string to slug format"""
        if not text:
            return ""
        
        # Convert to lowercase and replace spaces with hyphens
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')
    
    @staticmethod
    def pluralize(count, word):
        """Pluralize word based on count"""
        if count == 1:
            return f"{count} {word}"
        else:
            if word.endswith('y'):
                return f"{count} {word[:-1]}ies"
            elif word.endswith('s') or word.endswith('sh') or word.endswith('ch'):
                return f"{count} {word}es"
            elif word.endswith('f') or word.endswith('fe'):
                return f"{count} {word[:-1]}ves"
            else:
                return f"{count} {word}s"
    
    @staticmethod
    def ordinal(number):
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        try:
            num = int(number)
            if 11 <= (num % 100) <= 13:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
            return f"{num}{suffix}"
        except (ValueError, TypeError):
            return str(number)
    
    @staticmethod
    def format_initials(name):
        """Get initials from name"""
        if not name:
            return ""
        
        parts = name.split()
        initials = []
        
        for part in parts:
            if part:
                initials.append(part[0].upper())
        
        return ''.join(initials)
    
    @staticmethod
    def highlight_text(text, search_term, highlight_start='<mark>', highlight_end='</mark>'):
        """Highlight search term in text"""
        if not text or not search_term:
            return text
        
        # Escape special regex characters in search term
        escaped_term = re.escape(search_term)
        
        # Find and replace all occurrences
        pattern = re.compile(f'({escaped_term})', re.IGNORECASE)
        highlighted_text = pattern.sub(f'{highlight_start}\\1{highlight_end}', text)
        
        return highlighted_text
    
    @staticmethod
    def strip_html_tags(text):
        """Remove HTML tags from text"""
        if not text:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]*>', '', text)
        
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text.strip()
    
    @staticmethod
    def escape_html(text):
        """Escape HTML characters"""
        if not text:
            return ""
        
        html_escape_table = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        }
        
        for char, escape_seq in html_escape_table.items():
            text = text.replace(char, escape_seq)
        
        return text
    
    @staticmethod
    def url_encode(text):
        """URL encode text"""
        if not text:
            return ""
        
        import urllib.parse
        return urllib.parse.quote_plus(text)
    
    @staticmethod
    def url_decode(text):
        """URL decode text"""
        if not text:
            return ""
        
        import urllib.parse
        return urllib.parse.unquote_plus(text)
    
    @staticmethod
    def format_list(items, separator=', ', last_separator='and'):
        """Format list as string"""
        if not items:
            return ""
        
        if len(items) == 1:
            return str(items[0])
        elif len(items) == 2:
            return f"{items[0]} {last_separator} {items[1]}"
        else:
            return f"{separator.join(str(item) for item in items[:-1])} {last_separator} {items[-1]}"
    
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
    
    @staticmethod
    def format_relative_time(date_obj):
        """Format relative time (2 hours ago, etc.)"""
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
    def format_address(address_dict):
        """Format address dictionary"""
        if not address_dict:
            return ""
        
        parts = []
        
        if address_dict.get('street'):
            parts.append(address_dict['street'])
        
        if address_dict.get('city'):
            parts.append(address_dict['city'])
        
        if address_dict.get('state'):
            parts.append(address_dict['state'])
        
        if address_dict.get('zip'):
            parts.append(address_dict['zip'])
        
        if address_dict.get('country'):
            parts.append(address_dict['country'])
        
        return ', '.join(parts)
    
    @staticmethod
    def format_rating(rating, max_rating=5):
        """Format rating with stars"""
        try:
            rating_float = float(rating)
            full_stars = int(rating_float)
            half_star = rating_float - full_stars >= 0.5
            empty_stars = max_rating - full_stars - (1 if half_star else 0)
            
            stars = '★' * full_stars
            if half_star:
                stars += '½'
            stars += '☆' * empty_stars
            
            return f"{stars} ({rating_float:.1f})"
        except (ValueError, TypeError):
            return "☆☆☆☆☆ (0.0)"
    
    @staticmethod
    def format_percentage_bar(percentage, width=20):
        """Create percentage bar"""
        try:
            perc = float(percentage)
            filled = int((perc / 100) * width)
            empty = width - filled
            
            bar = '█' * filled + '░' * empty
            return f"{bar} {perc:.1f}%"
        except (ValueError, TypeError):
            return f"{'░' * width} 0.0%"

# Create instance
formatters = Formatters()
