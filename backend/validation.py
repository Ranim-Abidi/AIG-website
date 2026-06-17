"""
Form Validation Utilities
"""

import re
from datetime import datetime

DOB_FORMATS = ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y')

FACULTY_ALIASES = {
    'engineering': 'Engineering',
    'business': 'Business',
    'arts': 'Arts',
    'science': 'Science',
    'medicine': 'Medicine',
    'law': 'Law',
    'other': 'Other',
    'education': 'Education',
    'languages': 'Languages',
    'mathematics': 'Mathematics',
}


def normalize_faculty(faculty):
    """Map frontend faculty slugs to canonical names."""
    if not faculty:
        return faculty
    faculty = faculty.strip()
    if faculty in FACULTY_ALIASES:
        return FACULTY_ALIASES[faculty]
    if faculty == 'Arts & Humanities':
        return 'Arts'
    return faculty


def parse_dob(dob_str):
    """
    Parse a date of birth string into YYYY-MM-DD format.

    Returns:
        str or None
    """
    if not dob_str or not str(dob_str).strip():
        return None

    dob_str = str(dob_str).strip()
    for fmt in DOB_FORMATS:
        try:
            return datetime.strptime(dob_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def parse_phone(phone):
    """
    Parse a phone number into country code and local number for EXPA.

    Returns:
        dict: {'country_code': str, 'phone': str, 'digits': str}
    """
    if not phone:
        return {'country_code': '+30', 'phone': '', 'digits': ''}

    cleaned = re.sub(r'[\s\-().]', '', str(phone).strip())

    if cleaned.startswith('00'):
        cleaned = '+' + cleaned[2:]

    if cleaned.startswith('+'):
        if cleaned.startswith('+30') and len(cleaned) >= 12:
            return {
                'country_code': '+30',
                'phone': cleaned[3:],
                'digits': cleaned[1:],
            }
        if cleaned.startswith('+216') and len(cleaned) >= 11:
            return {
                'country_code': '+216',
                'phone': cleaned[4:],
                'digits': cleaned[1:],
            }
        if cleaned.startswith('+357') and len(cleaned) >= 11:
            return {
                'country_code': '+357',
                'phone': cleaned[4:],
                'digits': cleaned[1:],
            }
        digits = re.sub(r'\D', '', cleaned)
        if len(digits) >= 8:
            return {
                'country_code': '+30',
                'phone': digits,
                'digits': digits,
            }

    digits = re.sub(r'\D', '', cleaned)
    if len(digits) == 11 and digits.startswith('30'):
        return {'country_code': '+30', 'phone': digits[2:], 'digits': digits}
    if len(digits) == 12 and digits.startswith('216'):
        return {'country_code': '+216', 'phone': digits[3:], 'digits': digits}

    return {'country_code': '+30', 'phone': digits, 'digits': digits}


def normalize_form_data(data):
    """
    Normalize incoming form data before validation and submission.
    Mutates and returns the same dict for convenience.
    """
    normalized = dict(data)

    if normalized.get('firstName'):
        normalized['firstName'] = normalized['firstName'].strip()
    if normalized.get('lastName'):
        normalized['lastName'] = normalized['lastName'].strip()
    if normalized.get('email'):
        normalized['email'] = normalized['email'].strip().lower()

    if normalized.get('faculty'):
        normalized['faculty'] = normalize_faculty(normalized['faculty'])

    parsed_dob = parse_dob(normalized.get('dob', ''))
    if parsed_dob:
        normalized['dob'] = parsed_dob

    phone_parts = parse_phone(normalized.get('phone', ''))
    if phone_parts['phone']:
        normalized['phone'] = phone_parts['phone']
        normalized['country_code'] = phone_parts['country_code']

    return normalized


def validate_password(password):
    """
    Validate password strength according to EXPA requirements

    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    if len(password) < 8:
        return {'valid': False, 'error': 'Password must be at least 8 characters long'}

    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_number = bool(re.search(r'[0-9]', password))

    if not (has_upper and has_lower and has_number):
        return {
            'valid': False,
            'error': 'Password must contain uppercase, lowercase letters and at least one number'
        }

    return {'valid': True, 'error': None}


def validate_email(email):
    """
    Validate email format

    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    if len(email) < 4:
        return {'valid': False, 'error': 'Email is too short'}

    if ' ' in email:
        return {'valid': False, 'error': 'Email cannot contain spaces'}

    if '@' not in email or '.' not in email:
        return {'valid': False, 'error': 'Please enter a valid email address'}

    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return {'valid': False, 'error': 'Please enter a valid email address'}

    return {'valid': True, 'error': None}


def validate_phone(phone):
    """
    Validate phone number (local or international)

    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    phone_parts = parse_phone(phone)
    local_digits = re.sub(r'\D', '', phone_parts['phone'])

    if 8 <= len(local_digits) <= 15:
        return {'valid': True, 'error': None}

    return {'valid': False, 'error': 'Please enter a valid phone number'}


def calculate_age(dob_str):
    """
    Calculate age from date of birth string

    Args:
        dob_str (str): Date of birth in YYYY-MM-DD format

    Returns:
        int: Age in years
    """
    normalized_dob = parse_dob(dob_str)
    if not normalized_dob:
        return None

    try:
        dob = datetime.strptime(normalized_dob, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob.year

        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1

        return age
    except ValueError:
        return None


def validate_age(dob_str):
    """
    Validate age (must be between 18 and 30)

    Returns:
        dict: {'valid': bool, 'error': str or None, 'age': int or None}
    """
    normalized_dob = parse_dob(dob_str)
    if not normalized_dob:
        return {'valid': False, 'error': 'Please enter a valid date of birth', 'age': None}

    age = calculate_age(normalized_dob)

    if age is None:
        return {'valid': False, 'error': 'Please enter a valid date of birth', 'age': None}

    if age < 18:
        return {'valid': False, 'error': 'You must be at least 18 years old to apply', 'age': age}

    if age > 30:
        return {'valid': False, 'error': 'You must be 30 years or younger to apply', 'age': age}

    return {'valid': True, 'error': None, 'age': age}


def validate_form_data(data):
    """
    Validate all form fields

    Args:
        data (dict): Form data to validate

    Returns:
        dict: {'valid': bool, 'errors': dict}
    """
    data = normalize_form_data(data)
    errors = {}

    if not data.get('firstName') or not data['firstName'].strip():
        errors['firstName'] = 'First name is required'

    if not data.get('lastName') or not data['lastName'].strip():
        errors['lastName'] = 'Last name is required'

    email_validation = validate_email(data.get('email', ''))
    if not email_validation['valid']:
        errors['email'] = email_validation['error']

    password_validation = validate_password(data.get('password', ''))
    if not password_validation['valid']:
        errors['password'] = password_validation['error']

    phone_validation = validate_phone(data.get('phone', ''))
    if not phone_validation['valid']:
        errors['phone'] = phone_validation['error']

    age_validation = validate_age(data.get('dob', ''))
    if not age_validation['valid']:
        errors['dob'] = age_validation['error']

    if not data.get('campus') or data['campus'] == '':
        errors['campus'] = 'Please select a campus'

    if not data.get('faculty') or data['faculty'] == '':
        errors['faculty'] = 'Please select a faculty'

    if not data.get('preventReason') or data['preventReason'] == '':
        errors['preventReason'] = 'Please select a reason'

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
