import urllib.request
import urllib.parse
import http.cookiejar
import re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Public Visitor (Landing Page)
pub_res = opener.open('http://127.0.0.1:8000/')
pub_html = pub_res.read().decode('utf-8')
print('Public Page - Contains dropdown-toggle?:', 'dropdown-toggle' in pub_html)
print('Public Page - Clean single links present?:', all(x in pub_html for x in ['Overview', 'Pipeline', 'Intelligence', 'Impact']))

# 2. Authenticated Recruiter / Admin (Console Pages)
res = opener.open('http://127.0.0.1:8000/login/')
html = res.read().decode('utf-8')
token = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html).group(1)

data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': 'org.admin@talentiq.ai',
    'password': 'TalentIQAdmin2026!'
}).encode('utf-8')
opener.open('http://127.0.0.1:8000/login/', data=data)

auth_res = opener.open('http://127.0.0.1:8000/dashboard/')
auth_html = auth_res.read().decode('utf-8')
print('Recruiter Page - Has Platform AI Dropdown?:', 'id="platformDropdown"' in auth_html)
print('Recruiter Page - Has Recruitment Dropdown?:', 'id="recruitmentDropdown"' in auth_html)
print('Recruiter Page - Has Pipeline Flow & AI Intelligence items?:', 'Pipeline Flow' in auth_html and 'AI Intelligence' in auth_html)
print('Recruiter Page - Has Job Requisitions & Screen Resumes items?:', 'Job Requisitions' in auth_html and 'Screen Resumes' in auth_html)
