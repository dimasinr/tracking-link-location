import json
from datetime import date
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from tracking.models import TrackingLink, TrackingHit
from tracking.utils import get_ip_metadata, parse_user_agent, reverse_geocode
from tracking.views import get_client_ip

@csrf_exempt
def track_location(request):
    """
    POST /api/track/
    Body parameters:
    - code (str)
    - latitude (float)
    - longitude (float)
    - accuracy (float)
    - screen_width (int, optional)
    - screen_height (int, optional)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body'}, status=400)
        
    code = data.get('code')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')
    screen_width = data.get('screen_width')
    screen_height = data.get('screen_height')
    
    if not code:
        return JsonResponse({'success': False, 'error': 'Missing required parameter: code'}, status=400)
        
    # Get tracking link
    try:
        link = TrackingLink.objects.get(code=code)
    except TrackingLink.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tracking link not found'}, status=404)
        
    if not link.is_active:
        return JsonResponse({'success': False, 'error': 'Tracking link is inactive'}, status=400)
        
    if link.expired_at and link.expired_at < timezone.now():
        return JsonResponse({'success': False, 'error': 'Tracking link has expired'}, status=400)
        
    # Check IP
    ip = get_client_ip(request)
    
    # Resolve geographic location using coordinates (Nominatim)
    country, province, city, district, full_address = "", "", "", "", ""
    if latitude and longitude:
        country, province, city, district, full_address = reverse_geocode(latitude, longitude)
        
    # Get IP Metadata (ISP, ASN, fallbacks for country/city)
    ip_meta = get_ip_metadata(ip)
    
    # Fallback to IP country/city if reverse geocoding returns empty
    if not country or country == "Unknown":
        country = ip_meta.get('country', '')
    if not province or province == "Unknown":
        province = ip_meta.get('province', '')
    if not city or city == "Unknown":
        city = ip_meta.get('city', '')
        
    # User agent info
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    browser, browser_ver, os_name, dev_type = parse_user_agent(ua_string)
    
    # Create the hit record
    hit = TrackingHit.objects.create(
        tracking_link=link,
        ip_address=ip,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy,
        country=country,
        province=province,
        city=city,
        district=district,
        full_address=full_address,
        isp=ip_meta.get('isp'),
        asn=ip_meta.get('asn'),
        browser=browser,
        browser_version=browser_ver,
        os=os_name,
        device_type=dev_type,
        language=request.META.get('HTTP_ACCEPT_LANGUAGE', '')[:100],
        screen_width=screen_width,
        screen_height=screen_height,
        referrer=request.META.get('HTTP_REFERER', '')[:500]
    )
    
    return JsonResponse({'success': True, 'redirect_url': link.redirect_url or 'https://www.google.com'})

@login_required
def dashboard_stats_api(request):
    """
    GET /api/dashboard/stats/
    """
    user_links = TrackingLink.objects.filter(created_by=request.user)
    total_links = user_links.count()
    
    hits = TrackingHit.objects.filter(tracking_link__created_by=request.user)
    total_hits = hits.count()
    
    today = timezone.localdate()
    today_hits = hits.filter(visited_at__date=today).count()
    
    return JsonResponse({
        'total_links': total_links,
        'total_hits': total_hits,
        'today_hits': today_hits
    })
