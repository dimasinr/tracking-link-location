from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from tracking.models import TrackingLink, TrackingHit

@login_required
def dashboard_home(request):
    user = request.user
    
    # Base Querysets
    user_links = TrackingLink.objects.filter(created_by=user)
    user_hits = TrackingHit.objects.filter(tracking_link__created_by=user)
    
    # Card Stats
    total_links = user_links.count()
    total_hits = user_hits.count()
    active_links = user_links.filter(is_active=True).count()
    unique_visitors = user_hits.values('ip_address').distinct().count()
    today_hits = user_hits.filter(visited_at__date=timezone.localdate()).count()
    
    # Leaderboards
    top_countries = user_hits.values('country').annotate(count=Count('id')).order_by('-count')[:5]
    top_cities = user_hits.values('city').annotate(count=Count('id')).order_by('-count')[:5]
    most_accessed = user_links.annotate(count=Count('hits')).order_by('-count')[:5]
    
    # Latest Hits (20)
    latest_hits = user_hits.order_by('-visited_at')[:20]
    
    # Hits for Map (Hits that have coordinates)
    map_hits = user_hits.exclude(latitude__isnull=True, longitude__isnull=True).order_by('-visited_at')[:100]
    
    context = {
        'total_links': total_links,
        'total_hits': total_hits,
        'active_links': active_links,
        'unique_visitors': unique_visitors,
        'today_hits': today_hits,
        'top_countries': top_countries,
        'top_cities': top_cities,
        'most_accessed': most_accessed,
        'latest_hits': latest_hits,
        'map_hits': map_hits,
    }
    
    return render(request, 'dashboard/index.html', context)
