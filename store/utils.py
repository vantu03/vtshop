import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

def normalize_and_validate_phone(phone, region='VN'):
    try:
        parsed = phonenumbers.parse(phone, region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        pass
    return None
