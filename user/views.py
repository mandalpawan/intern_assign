import json
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

def GoogleCalendarInitView(request):
    params = {
        'response_type': 'code',
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri(reverse('google-calendar-redirect')),
        'scope': 'https://www.googleapis.com/auth/calendar.readonly',
        'access_type': 'offline',
    }
    auth_url = 'https://accounts.google.com/o/oauth2/auth?' + '&'.join([f'{key}={value}' for key, value in params.items()])
    print("ff",auth_url)
    return HttpResponseRedirect(auth_url)

def GoogleCalendarRedirectView(request):
    code = request.GET.get('code')
    print(code)
    if code:
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': request.build_absolute_uri(reverse('google-calendar-redirect')),
            'grant_type': 'authorization_code',
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            if access_token:
                events_url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json',
                }
                response = requests.get(events_url, headers=headers)
                if response.status_code == 200:
                    events = response.json().get('items', [])
                    return HttpResponse(json.dumps(events), content_type='application/json')
    
    return HttpResponse('Error: Failed to get access token')
