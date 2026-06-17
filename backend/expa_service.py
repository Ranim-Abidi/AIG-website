"""
EXPA API Service
Handles all communication with EXPA GraphQL API
"""

import requests
import logging

from .env_config import env, env_bool

logger = logging.getLogger(__name__)

EXPA_ENDPOINT = 'https://gis-api.aiesec.org/graphql'
EXPA_AUTH_URL = 'https://auth.aiesec.org/users.json'
EXPA_API_TOKEN = env('EXPA_API_TOKEN', '')
EXPA_VERIFY_SSL = env_bool('EXPA_VERIFY_SSL', True)


def check_email_unique(email):
    """
    Check if an email is unique in EXPA system
    Note: EXPA REST API doesn't have a separate email check endpoint,
    so we just return True and let the signup handle duplicates

    Args:
        email (str): Email address to check

    Returns:
        dict: {'unique': bool, 'error': str or None}
    """
    logger.info(f"Email check for {email} - skipping validation (will be checked during signup)")
    return {'unique': True, 'error': None}


def _friendly_expa_message(field, message):
    """Map EXPA validation messages to user-friendly copy."""
    text = str(message)
    lower = text.lower()

    if field == 'email' and ('taken' in lower or 'already' in lower):
        return 'This email is already registered. Please sign in or use a different email.'

    if field == 'password':
        return f'Password: {text}'

    if field == 'phone':
        return f'Phone: {text}'

    if field in text.lower():
        return text

    return f'{field.replace("_", " ").title()}: {text}'


def _parse_expa_errors(errors_dict):
    """
    Parse EXPA errors object into field-level errors and a summary string.

    Returns:
        tuple: (field_errors dict, summary str)
    """
    field_errors = {}
    summary_parts = []

    for field, messages in errors_dict.items():
        if isinstance(messages, list):
            message = messages[0] if messages else 'Invalid value'
        else:
            message = str(messages)

        friendly = _friendly_expa_message(field, message)
        field_errors[field] = friendly
        summary_parts.append(friendly)

    return field_errors, '; '.join(summary_parts)


def _post_expa_user(payload):
    """
    POST a user signup payload to EXPA and normalize the response.

    Returns:
        dict with keys: success, data, person_id, error, errors, status_code
    """
    try:
        response = requests.post(
            EXPA_AUTH_URL,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30,
            verify=EXPA_VERIFY_SSL,
        )

        try:
            result = response.json()
        except ValueError:
            result = {}

        logger.info(f"EXPA REST API status={response.status_code}")

        if response.status_code >= 400:
            if result.get('errors'):
                field_errors, error_str = _parse_expa_errors(result['errors'])
                logger.error(f"EXPA signup errors: {error_str}")
                return {
                    'success': False,
                    'data': None,
                    'person_id': None,
                    'error': error_str,
                    'errors': field_errors,
                    'status_code': 400 if response.status_code in (400, 422) else 502,
                }

            logger.error(f"EXPA signup failed: HTTP {response.status_code} - {response.text[:300]}")
            return {
                'success': False,
                'data': None,
                'person_id': None,
                'error': 'EXPA signup failed. Please try again later.',
                'errors': {},
                'status_code': 502 if response.status_code >= 500 else 400,
            }

        if result.get('errors'):
            field_errors, error_str = _parse_expa_errors(result['errors'])
            logger.error(f"EXPA signup errors: {error_str}")
            return {
                'success': False,
                'data': None,
                'person_id': None,
                'error': error_str,
                'errors': field_errors,
                'status_code': 400,
            }

        person_id = result.get('person_id')
        if person_id:
            return {
                'success': True,
                'data': {'person_id': person_id, 'applicant': result},
                'person_id': person_id,
                'error': None,
                'errors': {},
                'status_code': 200,
            }

        return {
            'success': False,
            'data': None,
            'person_id': None,
            'error': 'No account ID returned from EXPA. Please contact support.',
            'errors': {},
            'status_code': 502,
        }

    except requests.exceptions.Timeout:
        logger.error("EXPA API timeout")
        return {
            'success': False,
            'data': None,
            'person_id': None,
            'error': 'Request timeout. Please try again.',
            'errors': {},
            'status_code': 504,
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during signup: {str(e)}")
        return {
            'success': False,
            'data': None,
            'person_id': None,
            'error': 'Could not reach EXPA. Check your connection and try again.',
            'errors': {},
            'status_code': 503,
        }
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        return {
            'success': False,
            'data': None,
            'person_id': None,
            'error': 'Unexpected error occurred',
            'errors': {},
            'status_code': 500,
        }


def submit_global_volunteer_signup(data):
    """
    Submit Global Volunteer signup to EXPA using REST API
    Based on the old PHP implementation

    Args:
        data (dict): Signup data containing all required fields

    Returns:
        dict: {'success': bool, 'data': dict or None, 'error': str or None, ...}
    """
    from .validation import parse_phone

    phone_parts = parse_phone(data.get('phone', ''))
    country_code = data.get('country_code') or phone_parts['country_code']
    phone_number = phone_parts['phone'] or data.get('phone', '')

    payload = {
        "user": {
            "first_name": data['firstname'],
            "last_name": data['lastname'],
            "email": data['email'],
            "password": data['password'],
            "phone": phone_number,
            "country_code": country_code,
            "lc": data['campus'],
            "mc": 1555,
            "allow_phone_communication": "true",
            "allow_email_communication": "true"
        }
    }

    return _post_expa_user(payload)


def submit_member_signup(data):
    """
    Submit Member signup to EXPA using REST API

    Args:
        data (dict): Signup data containing all required fields

    Returns:
        dict: {'success': bool, 'person_id': int or None, 'error': str or None, ...}
    """
    from .validation import parse_phone

    phone_parts = parse_phone(data.get('phone', ''))
    country_code = data.get('country_code') or phone_parts['country_code']
    phone_number = phone_parts['phone'] or data.get('phone', '')

    payload = {
        "user": {
            "first_name": data['firstName'],
            "last_name": data['lastName'],
            "email": data['email'],
            "password": data['password'],
            "phone": phone_number,
            "country_code": country_code,
            "lc": data['lc_id'],
            "mc": 1555,
            "allow_phone_communication": "true",
            "allow_email_communication": "true",
            "why_would_you_like_to_join_aiesec": data.get('whyJoin', '')
        }
    }

    result = _post_expa_user(payload)
    if result['success']:
        return {
            'success': True,
            'person_id': result['person_id'],
            'error': None,
            'errors': {},
            'status_code': 200,
        }

    return {
        'success': False,
        'person_id': None,
        'error': result.get('error'),
        'errors': result.get('errors', {}),
        'status_code': result.get('status_code', 500),
    }
