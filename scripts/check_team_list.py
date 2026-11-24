import urllib.request
import urllib.parse
import http.cookiejar
import re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

res = opener.open('http://127.0.0.1:8000/login/')
html = res.read().decode('utf-8')
token = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html).group(1)

data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': 'org.admin@talentiq.ai',
    'password': 'TalentIQAdmin2026!'
}).encode('utf-8')
opener.open('http://127.0.0.1:8000/login/', data=data)

team_res = opener.open('http://127.0.0.1:8000/organization/team/')
team_html = team_res.read().decode('utf-8')

print("Present in Team Recruiters list:")
print("thanigaivelk.official@gmail.com ->", "thanigaivelk.official@gmail.com" in team_html)
print("thanigaivel.kannan@talentiq.ai ->", "thanigaivel.kannan@talentiq.ai" in team_html)
print("org.admin@talentiq.ai ->", "org.admin@talentiq.ai" in team_html)
