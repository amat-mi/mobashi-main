from django.core.cache import cache
from django.http import HttpResponse
import re
from .utils import build_qrcode


def qrcode_view(request, key=None):
    """
    From: https://github.com/kangasbros/django-bitcoin/blob/master/django_bitcoin/views.py
    Modified to get a few parameters from the query string ('box_size', etc.)
    If no key specified, use the referer URL, that is, the page that is calling this view
    If a query param "path" exists, use that as key, after making it absolute through build_absolute_uri()
    In the end if no key was constructed, use the absolute url of this request itself 
    """
    # In some cases (FastCGI, flup or others) double slashes gets removed before being passed as "key"
    # Since we're using QR codes for URLS, double slashes are important, so try to recreate them when needed
    key = re.sub(r'^http:/([^/]+.*$)', r'http://\1', key) if key is not None \
        else request.META.get('HTTP_REFERER', None)

    path = request.GET.get('path', None)
    if path:
        key = request.build_absolute_uri(path)

    if key is None:
        key = request.build_absolute_uri()

    res = build_qrcode(
        key,
        box_size=request.GET.get('box_size', 2),
        border=request.GET.get('border', 4),
        error_correction=request.GET.get('error_correction', 'M'),
        output_format='PNG',
        use_cache=True)
    return HttpResponse(res, content_type="image/png")
