import re
import requests

def parse_user_agent(user_agent_string):
    """
    Parses User Agent string to extract browser, version, OS, and device type.
    """
    if not user_agent_string:
        return "Unknown", "Unknown", "Unknown", "Desktop"

    # Default values
    browser = "Unknown Browser"
    version = "Unknown"
    os_name = "Unknown OS"
    device_type = "Desktop"

    ua = user_agent_string.lower()

    # Device type detection
    if "mobi" in ua or "iphone" in ua or "ipod" in ua:
        device_type = "Mobile"
    elif "ipad" in ua or "tablet" in ua or "playbook" in ua:
        device_type = "Tablet"
    else:
        device_type = "Desktop"

    # OS detection
    if "windows" in ua:
        os_name = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        os_name = "macOS"
    elif "iphone" in ua or "ipad" in ua or "ipod" in ua:
        os_name = "iOS"
    elif "android" in ua:
        os_name = "Android"
    elif "linux" in ua:
        os_name = "Linux"

    # Browser detection
    if "edg/" in ua or "edge/" in ua:
        browser = "Edge"
        match = re.search(r'(?:edg|edge)/([\d\.]+)', ua)
        if match:
            version = match.group(1)
    elif "opr/" in ua or "opera/" in ua:
        browser = "Opera"
        match = re.search(r'(?:opr|opera)/([\d\.]+)', ua)
        if match:
            version = match.group(1)
    elif "chrome/" in ua:
        browser = "Chrome"
        match = re.search(r'chrome/([\d\.]+)', ua)
        if match:
            version = match.group(1)
    elif "safari/" in ua:
        browser = "Safari"
        match = re.search(r'version/([\d\.]+)', ua)
        if match:
            version = match.group(1)
    elif "firefox/" in ua:
        browser = "Firefox"
        match = re.search(r'firefox/([\d\.]+)', ua)
        if match:
            version = match.group(1)

    return browser, version[:20], os_name, device_type


def get_ip_metadata(ip):
    """
    Fetches network & ISP information from ip-api.com.
    Returns dictionary with country, province (region), city, isp, asn.
    Includes mock fallback for localhost/private IPs.
    """
    # Mock data for local testing
    if ip in ["127.0.0.1", "localhost", "::1"] or ip.startswith("192.168.") or ip.startswith("10."):
        return {
            "country": "Indonesia",
            "province": "Jakarta",
            "city": "South Jakarta",
            "isp": "Telkom Indonesia",
            "asn": "AS7713 PT Telekomunikasi Indonesia"
        }

    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "country": data.get("country", ""),
                    "province": data.get("regionName", ""),
                    "city": data.get("city", ""),
                    "isp": data.get("isp", ""),
                    "asn": data.get("as", "")
                }
    except Exception as e:
        print(f"Error fetching IP metadata: {e}")

    return {
        "country": "Unknown",
        "province": "Unknown",
        "city": "Unknown",
        "isp": "Unknown",
        "asn": "Unknown"
    }


def reverse_geocode(lat, lon):
    """
    Uses OpenStreetMap's Nominatim API to convert coordinates to a readable address.
    """
    if not lat or not lon:
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

    try:
        # Nominatim requires a user-agent to prevent HTTP 403
        headers = {
            "User-Agent": "GPSTrackingPlatform/1.0 (contact@example.com)"
        }
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address_info = data.get("address", {})
            
            country = address_info.get("country", "")
            province = address_info.get("state", address_info.get("region", ""))
            city = address_info.get("city", address_info.get("town", address_info.get("village", "")))
            district = address_info.get("suburb", address_info.get("city_district", address_info.get("county", "")))
            full_address = data.get("display_name", "")
            
            return country, province, city, district, full_address
    except Exception as e:
        print(f"Error reverse geocoding: {e}")

    return "", "", "", "", ""
