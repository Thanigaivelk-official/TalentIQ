import urllib.request
import urllib.parse
import http.cookiejar
import re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
res = opener.open('http://127.0.0.1:8000/login/')
html = res.read().decode('utf-8')
token = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html).group(1)

data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'username': 'org.admin@talentiq.ai',
    'password': 'TalentIQAdmin2026!'
}).encode('utf-8')
opener.open('http://127.0.0.1:8000/login/', data=data)

# Team page
team_res = opener.open('http://127.0.0.1:8000/organization/team/')
team_html = team_res.read().decode('utf-8')
token2 = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', team_html).group(1)

# Find user ID
matches = re.findall(r'data-user-id=["\']([^"\']+)["\'][^>]*data-email=["\']([^"\']+)["\']', team_html)
print("Found team recruiters:", matches)
for uid, mail in matches:
    if 'recruiter' in mail or 'kannan' in mail:
        target_uid = uid
        break
else:
    target_uid = matches[-1][0]

# Submit update
edit_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token2,
    'action': 'edit',
    'user_id': target_uid,
    'first_name': 'Thanigaivel',
    'last_name': 'Kannan',
    'email': 'thanigaivel.kannan@talentiq.ai',
    'title': 'Principal Technical Recruiter',
    'department': 'Human Resources',
    'role': 'RECRUITER',
    'new_password': ''
}).encode('utf-8')

post_res = opener.open('http://127.0.0.1:8000/organization/team/', data=edit_data)
updated_html = post_res.read().decode('utf-8')

if 'thanigaivel.kannan@talentiq.ai' in updated_html:
    print('SUCCESS: Email field is editable, saved, and rendered live in the UI!')
else:
    print('Check output')
