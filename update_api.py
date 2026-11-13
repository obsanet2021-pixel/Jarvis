with open(r'C:\Users\Free user\Jarvis\api\main.py', 'r', encoding='utf-8') as f:
    code = f.read()

auth_imports = '''
from fastapi import Header, Request
from api.auth import token_manager
import collections

REQUEST_LIMITS = collections.defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else 'unknown'
    now = time.time()
    requests = REQUEST_LIMITS[client_ip]
    while requests and requests[0] < now - RATE_LIMIT_WINDOW:
        requests.pop(0)
    if len(requests) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail='Rate limit exceeded. Try again later.')
    requests.append(now)

def verify_auth(x_jarvis_auth: Optional[str] = Header(None)):
    if not x_jarvis_auth:
        return 'anonymous'
    user_id = token_manager.verify_token(x_jarvis_auth)
    if not user_id:
        raise HTTPException(status_code=401, detail='Invalid or expired authentication token')
    return user_id
'''

if 'check_rate_limit' not in code:
    code = code.replace('from core.ussd import USSDManager', 'from core.ussd import USSDManager\n' + auth_imports)
    code = code.replace('@app.post("/call")', '@app.post("/call", dependencies=[Depends(check_rate_limit), Depends(verify_auth)])')
    code = code.replace('@app.post("/ussd/balance")', '@app.post("/ussd/balance", dependencies=[Depends(check_rate_limit), Depends(verify_auth)])')

    with open(r'C:\Users\Free user\Jarvis\api\main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print('Updated api/main.py successfully!')
else:
    print('Already updated!')
