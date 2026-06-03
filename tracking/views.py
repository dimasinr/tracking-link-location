import csv
import openpyxl
from datetime import datetime
from django.shortcuts import render, redirect, get_list_or_404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.utils.crypto import get_random_string

from .models import TrackingLink, TrackingHit
from .utils import get_ip_metadata, parse_user_agent, reverse_geocode

@login_required
def link_list(request):
    links = TrackingLink.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Calculate hit count annotation manually or via annotate
    links = links.annotate(hit_count=Count('hits'))
    
    return render(request, 'tracking/list.html', {'links': links})

@login_required
def link_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        redirect_url = request.POST.get('redirect_url', '')
        require_gps = request.POST.get('require_gps') == 'true'
        expired_at_str = request.POST.get('expired_at', '')
        
        # Generate unique code
        code = get_random_string(8).upper()
        while TrackingLink.objects.filter(code=code).exists():
            code = get_random_string(8).upper()
            
        expired_at = None
        if expired_at_str:
            try:
                expired_at = datetime.strptime(expired_at_str, '%Y-%m-%dT%H:%M')
                expired_at = timezone.make_aware(expired_at)
            except ValueError:
                pass
                
        link = TrackingLink.objects.create(
            name=name,
            description=description,
            code=code,
            require_gps=require_gps,
            redirect_url=redirect_url,
            expired_at=expired_at,
            created_by=request.user
        )
        return redirect('link_list')
        
    return render(request, 'tracking/create.html')

@login_required
def link_toggle(request, pk):
    link = get_object_or_404(TrackingLink, pk=pk, created_by=request.user)
    link.is_active = not link.is_active
    link.save()
    return redirect('link_list')

@login_required
def link_delete(request, pk):
    link = get_object_or_404(TrackingLink, pk=pk, created_by=request.user)
    link.delete()
    return redirect('link_list')

@login_required
def result_list(request):
    hits = TrackingHit.objects.filter(tracking_link__created_by=request.user).order_by('-visited_at')
    
    # Filter operations
    link_id = request.GET.get('link')
    country = request.GET.get('country')
    city = request.GET.get('city')
    ip = request.GET.get('ip')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if link_id:
        hits = hits.filter(tracking_link_id=link_id)
    if country:
        hits = hits.filter(country__icontains=country)
    if city:
        hits = hits.filter(city__icontains=city)
    if ip:
        hits = hits.filter(ip_address__icontains=ip)
        
    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d')
            hits = hits.filter(visited_at__date__gte=sd)
        except ValueError:
            pass
            
    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d')
            hits = hits.filter(visited_at__date__lte=ed)
        except ValueError:
            pass

    # For filter options
    user_links = TrackingLink.objects.filter(created_by=request.user)
    
    context = {
        'hits': hits,
        'user_links': user_links,
        'selected_link': link_id,
        'selected_country': country or '',
        'selected_city': city or '',
        'selected_ip': ip or '',
        'start_date': start_date or '',
        'end_date': end_date or ''
    }
    return render(request, 'tracking/results.html', context)

@login_required
def result_detail(request, pk):
    hit = get_object_or_404(TrackingHit, pk=pk, tracking_link__created_by=request.user)
    return render(request, 'tracking/detail.html', {'hit': hit})

def consent_view(request, code):
    link = get_object_or_404(TrackingLink, code=code)
    
    # Validation checks
    if not link.is_active:
        return render(request, 'tracking/consent.html', {
            'error_message': 'This link is currently inactive.',
            'link': link
        })
        
    if link.expired_at and link.expired_at < timezone.now():
        return render(request, 'tracking/consent.html', {
            'error_message': 'This link has expired.',
            'link': link
        })
        
    # If the link doesn't require GPS, perform direct background tracking and redirect
    if not link.require_gps:
        # Get client IP and metadata
        ip = get_client_ip(request)
        ip_meta = get_ip_metadata(ip)
        
        ua_string = request.META.get('HTTP_USER_AGENT', '')
        browser, browser_ver, os_name, dev_type = parse_user_agent(ua_string)
        
        hit = TrackingHit.objects.create(
            tracking_link=link,
            ip_address=ip,
            country=ip_meta.get('country'),
            province=ip_meta.get('province'),
            city=ip_meta.get('city'),
            isp=ip_meta.get('isp'),
            asn=ip_meta.get('asn'),
            browser=browser,
            browser_version=browser_ver,
            os=os_name,
            device_type=dev_type,
            language=request.META.get('HTTP_ACCEPT_LANGUAGE', '')[:100],
            referrer=request.META.get('HTTP_REFERER', '')[:500]
        )
        
        redirect_to = link.redirect_url or 'https://www.google.com'
        return redirect(redirect_to)
        
    return render(request, 'tracking/consent.html', {'link': link})

# Helper function
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def export_hits_csv(request):
    hits = TrackingHit.objects.filter(tracking_link__created_by=request.user).order_by('-visited_at')
    
    # Filter similarly
    link_id = request.GET.get('link')
    country = request.GET.get('country')
    city = request.GET.get('city')
    ip = request.GET.get('ip')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if link_id:
        hits = hits.filter(tracking_link_id=link_id)
    if country:
        hits = hits.filter(country__icontains=country)
    if city:
        hits = hits.filter(city__icontains=city)
    if ip:
        hits = hits.filter(ip_address__icontains=ip)
    if start_date:
        hits = hits.filter(visited_at__date__gte=datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        hits = hits.filter(visited_at__date__lte=datetime.strptime(end_date, '%Y-%m-%d'))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tracking_hits_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date/Time', 'Link Name', 'Code', 'IP Address', 'Latitude', 'Longitude', 
        'Accuracy (m)', 'Country', 'Province', 'City', 'District', 'Full Address', 
        'ISP', 'ASN', 'Browser', 'OS', 'Device Type', 'Language', 'Referrer'
    ])
    
    for hit in hits:
        writer.writerow([
            hit.visited_at.strftime('%Y-%m-%d %H:%M:%S'),
            hit.tracking_link.name,
            hit.tracking_link.code,
            hit.ip_address,
            hit.latitude or '',
            hit.longitude or '',
            hit.accuracy or '',
            hit.country or '',
            hit.province or '',
            hit.city or '',
            hit.district or '',
            hit.full_address or '',
            hit.isp or '',
            hit.asn or '',
            hit.browser or '',
            hit.os or '',
            hit.device_type or '',
            hit.language or '',
            hit.referrer or ''
        ])
        
    return response

@login_required
def export_hits_excel(request):
    hits = TrackingHit.objects.filter(tracking_link__created_by=request.user).order_by('-visited_at')
    
    # Filter similarly
    link_id = request.GET.get('link')
    country = request.GET.get('country')
    city = request.GET.get('city')
    ip = request.GET.get('ip')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if link_id:
        hits = hits.filter(tracking_link_id=link_id)
    if country:
        hits = hits.filter(country__icontains=country)
    if city:
        hits = hits.filter(city__icontains=city)
    if ip:
        hits = hits.filter(ip_address__icontains=ip)
    if start_date:
        hits = hits.filter(visited_at__date__gte=datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        hits = hits.filter(visited_at__date__lte=datetime.strptime(end_date, '%Y-%m-%d'))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tracking Hits"
    
    headers = [
        'Date/Time', 'Link Name', 'Code', 'IP Address', 'Latitude', 'Longitude', 
        'Accuracy (m)', 'Country', 'Province', 'City', 'District', 'Full Address', 
        'ISP', 'ASN', 'Browser', 'OS', 'Device Type', 'Language', 'Referrer'
    ]
    ws.append(headers)
    
    for hit in hits:
        ws.append([
            hit.visited_at.strftime('%Y-%m-%d %H:%M:%S'),
            hit.tracking_link.name,
            hit.tracking_link.code,
            hit.ip_address,
            float(hit.latitude) if hit.latitude else '',
            float(hit.longitude) if hit.longitude else '',
            hit.accuracy or '',
            hit.country or '',
            hit.province or '',
            hit.city or '',
            hit.district or '',
            hit.full_address or '',
            hit.isp or '',
            hit.asn or '',
            hit.browser or '',
            hit.os or '',
            hit.device_type or '',
            hit.language or '',
            hit.referrer or ''
        ])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="tracking_hits_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    wb.save(response)
    
    return response
