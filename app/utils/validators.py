import re
import secrets
import string
from datetime import datetime, timedelta

class Validators:
    @staticmethod
    def is_valid_email(email):
        """Validate email format"""
        if not email:
            return False
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return re.match(email_regex, email) is not None
    
    @staticmethod
    def is_valid_password(password):
        """Validate password strength"""
        if not password or len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:"<>,.?/]', password):
            return False
        return True
    
    @staticmethod
    def is_valid_name(name):
        """Validate name format"""
        if not name or len(name.strip()) < 2:
            return False
        name_regex = r'^[a-zA-Z\s\'\-]+$'
        return re.match(name_regex, name) is not None
    
    @staticmethod
    def is_valid_phone(phone):
        """Validate phone number format"""
        if not phone:
            return False
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) in [10, 11]
    
    @staticmethod
    def is_valid_url(url):
        """Validate URL format"""
        if not url:
            return False
        url_regex = r'^https?://(?:[-\w.]+(?:\.[a-z0-9.-]+\.[a-z]{2,})(?:/[-\w./?%&=]*)?$'
        return re.match(url_regex, url) is not None
    
    @staticmethod
    def is_valid_date(date_string, date_format='%Y-%m-%d'):
        """Validate date string format"""
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_credit_card(card_number):
        """Validate credit card number using Luhn algorithm"""
        if not card_number:
            return False
        digits = re.sub(r'[\s-]', '', card_number)
        if not digits.isdigit() or len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn algorithm
        total = 0
        num_digits = len(digits)
        parity = num_digits % 2
        
        for i, digit in enumerate(digits):
            int_digit = int(digit)
            if i % 2 == parity:
                total += int_digit
            else:
                total += int_digit * 2
        
        return total % 10 == 0
    
    @staticmethod
    def is_valid_expiry_date(expiry_date):
        """Validate credit card expiry date (MM/YY)"""
        if not expiry_date:
            return False
        expiry_regex = r'^(0[1-9]|1[0-2])/\d{2}$'
        if not re.match(expiry_regex, expiry_date):
            return False
        
        try:
            month, year = expiry_date.split('/')
            month = int(month)
            year = int(year)
            current_year = datetime.now().year % 100
            full_year = 2000 + year
            if year < current_year:
                full_year += 100
            expiry_datetime = datetime(full_year, month, 1)
            return expiry_datetime > datetime.now()
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def is_valid_cvv(cvv):
        """Validate CVV (3 or 4 digits)"""
        if not cvv:
            return False
        cvv_regex = r'^\d{3,4}$'
        return re.match(cvv_regex, cvv) is not None
    
    @staticmethod
    def is_valid_project_title(title):
        """Validate project title"""
        if not title or len(title.strip()) < 3 or len(title.strip()) > 200:
            return False
        title_regex = r'^[a-zA-Z0-9\s\-\.,\'\(\)]+$'
        return re.match(title_regex, title) is not None
    
    @staticmethod
    def is_valid_research_field(field):
        """Validate research field"""
        valid_fields = ['computer-science', 'engineering', 'medicine', 'business', 'education', 'social-sciences', 'natural-sciences', 'other']
        return field in valid_fields
    
    @staticmethod
    def is_valid_priority(priority):
        """Validate priority level"""
        return priority in ['low', 'medium', 'high']
    
    @staticmethod
    def is_valid_status(status):
        """Validate project status"""
        return status in ['pending', 'in_progress', 'completed', 'payment_required', 'cancelled', 'archived']
    
    @staticmethod
    def validate_file_size(file_size, min_size=0, max_size=None):
        """Validate file size"""
        if max_size is None:
            max_size = 16 * 1024 * 1024  # 16MB default
        if file_size < min_size:
            return False, f"File size must be at least {min_size} bytes"
        if file_size > max_size:
            return False, f"File size must be no more than {max_size} bytes"
        return True, None
    
    @staticmethod
    def is_safe_filename(filename):
        """Check if filename is safe"""
        if not filename:
            return False
        dangerous_patterns = ['../', '..\\', '/', '\\', '|', ';', '<', '>', '"', "'", '`', '$', '(', ')', '{', '}', '%', '!']
        for pattern in dangerous_patterns:
            if pattern in filename:
                return False
        return True
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename"""
        if not filename:
            return ''
        dangerous_chars = ['../', '..\\', '/', '\\', '|', ';', '<', '>', '"', "'", '`', '$', '(', ')', '{', '}', '%', '!']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        filename = re.sub(r'_+', '_', filename)
        return filename.strip('_')
    
    @staticmethod
    def is_valid_price(price):
        """Validate price format"""
        try:
            return float(price) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_rating(rating, min_rating=0, max_rating=5):
        """Validate rating"""
        try:
            rating_float = float(rating)
            return min_rating <= rating_float <= max_rating
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def generate_token(length=32):
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_otp(length=6):
        """Generate OTP code"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))

# Create instance
validators = Validators()
