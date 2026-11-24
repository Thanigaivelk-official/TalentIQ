import urllib.request
import urllib.parse
import http.cookiejar
import re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# GET login page
res = opener.open('http://127.0.0.1:8000/login/')
html = res.read().decode('utf-8')
match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html)
token = match.group(1) if match else ''

# POST login
data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': 'demo.recruiter@talentiq.ai',
    'password': 'TalentIQDemo2026!'
}).encode('utf-8')
login_res = opener.open('http://127.0.0.1:8000/login/', data=data)

# GET dashboard
dash_res = opener.open('http://127.0.0.1:8000/dashboard/')
dash_html = dash_res.read().decode('utf-8')
print("Status:", dash_res.status)
print("Dashboard HTML Preview (first 1000 chars):")
print(dash_html[:1000])
