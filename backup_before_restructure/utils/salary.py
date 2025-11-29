import re
from decimal import Decimal

CURRENCY_SYMBOLS = {
    "$":"USD",
    "₹":"INR",
    "Rs":"INR",
    "EUR":"EUR",
    "£":"GBP"
}

def extract_salary(text):
    # find patterns like "₹20,00,000 - ₹30,00,000 a year" or "$80,000 - $120,000 a year"
    regex = r'([\₹\$\£\€]?\s?\d[\d\,\.]*(?:k|K|,|\.\d+)*)(?:\s*-\s*([\₹\$\£\€]?\s?\d[\d\,\.]*(?:k|K|,|\.\d+)*))?.{0,30}(per year|a year|per annum|/year|per month|a month|/month|hour|per hour|/hr|hr)'
    m = re.search(regex, text, flags=re.I)
    if not m:
        return None
    s1 = m.group(1)
    s2 = m.group(2)
    period = m.group(3).lower() if m.group(3) else "year"
    def parse_num(s):
        if not s: return None
        s = s.replace(",","").replace(" ","")
        if s.lower().endswith("k"):
            return float(s[:-1]) * 1000
        # remove currency symbol
        s = re.sub(r'[^\d\.]','', s)
        try:
            return float(s)
        except:
            return None
    minv = parse_num(s1)
    maxv = parse_num(s2) if s2 else minv
    # normalize to annual if monthly/hourly found
    if "month" in period:
        minv = minv * 12 if minv else None
        maxv = maxv * 12 if maxv else None
    if "hour" in period or "hr" in period:
        minv = minv * 2080 if minv else None
        maxv = maxv * 2080 if maxv else None
    return {"min":minv, "max":maxv, "period":period}
