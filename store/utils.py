import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse

def normalize_and_validate_phone(phone, region='VN'):
    try:
        parsed = phonenumbers.parse(phone, region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        pass
    return None

def update_url_query(url, updates={}, removes=[]):
    parts = urlparse(url)
    query = parse_qs(parts.query)

    # Cập nhật
    for key, value in updates.items():
        query[key] = [value]

    # Xóa
    for key in removes:
        query.pop(key, None)

    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parts._replace(query=new_query))
    return new_url
