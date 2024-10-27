"""Web service for libem"""

import os
import uvicorn
import mysql.connector

from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi_login import LoginManager
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from pydantic import BaseModel

import libem

file_path = os.path.dirname(os.path.abspath(__file__))


#####################
# POST structs
#####################

class Match(BaseModel):
    left: str | list[str]
    right: str | list[str]
    config: dict[str, str] | None = None
class RunSql(BaseModel):
    query: str
    password: str


#####################
# SQL DB
#####################

def connect_sql():
    return mysql.connector.connect(user='mysql', password='password',
                                   host=os.getenv('MYSQL_IP'),
                                   database='serve')

con = connect_sql()
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users("
            "id varchar(30) NOT null PRIMARY KEY, "
            "email varchar(200), "
            "name varchar(200), "
            "avatar varchar(200), "
            "credits int)")
cur.close()


#####################
# OAuth
#####################

# load .env if needed
if not os.getenv('SECRET'):
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(file_path), 'serve.env')
    load_dotenv(env_path)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

SECRET = os.getenv('SECRET')
manager = LoginManager(SECRET, token_url='/login', use_cookie=True)

class NotAuthenticatedException(Exception):
    pass


#####################
# Helpers
#####################

def register_user(user: dict):
    sub = user['sub']
    
    # add user to db
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (sub,))
    existing = cur.fetchall()
    if len(existing) == 0:
        cur.execute("INSERT INTO users(id, name, email, avatar, credits) VALUES(%s, %s, %s, %s, %s)",
                    (sub, user['name'], user['email'], user['picture'], os.getenv('TRIAL_CREDITS')))
        con.commit()
    cur.close()
    
    # generate access token
    access_token = manager.create_access_token(
        data=dict(sub=sub),
        expires=timedelta(days=30)
    )
    
    return access_token


#####################
# FastAPI
#####################

description = '''
Libem Serve.
'''

tags_metadata = []

app = FastAPI(
    title="Libem Serve",
    description=description,
    openapi_tags=tags_metadata
)

app.add_middleware(SessionMiddleware, secret_key=SECRET)

# handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# fetch user data once authenticated
@manager.user_loader()
def load_user(user_id: str):
    con = connect_sql()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchall()
    cur.close()
    
    if len(user) == 0:
        return None
    
    return user[0]


@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    return JSONResponse(
        status_code=401,
        content="Authentication token expired or invalid. "
                "Try logging in again from your browser at "
                "https://serve.libem.org."
    )


@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(os.path.join(file_path, 'index.html'))


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(file_path, 'favicon.ico'))
    

@app.get("/login", tags=["Authentication"])
async def login(request: Request):
    if os.getenv('OFFLINE_MODE') == 'true':
        # generate 'fake' user info
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS count FROM users")
        user_count = cur.fetchall()[0]
        con.commit()
        cur.close()
        
        user_id = user_count['count'] + 1
        user = {
            'sub': user_id,
            'name': f'Offline User {user_id}',
            'email': f'offline_user{user_id}@example.com',
            'picture': None,
        }
        
        access_token = register_user(user)
        return RedirectResponse(f'/?auth={access_token}')
    else:
        # absolute url for callback
        redirect_uri = request.url_for('auth')
        return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth", include_in_schema=False)
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return RedirectResponse(f'/')
    
    user = token.get('userinfo')
    access_token = register_user(user)
    
    return RedirectResponse(f'/?auth={access_token}')


@app.get("/profile", include_in_schema=False)
def profile(user=Depends(manager)):
    return JSONResponse({
        'name': user['name'],
        'avatar': user['avatar'],
        'email': user['email'],
        'credits': user['credits']
        })
    

@app.get("/credits", tags=["API"])
def credits(user=Depends(manager)):
    return JSONResponse({
        'credits': user['credits']
    })


@app.post("/match", tags=["API"])
def match(data: Match, user=Depends(manager)):
    def record_length(data: str | list[str]):
        if type(data) == list:
            return sum(record_length(record) for record in data)
        return len(data)
    
    # estimate token usage and reject if not enough credits
    tokens_needed = (record_length(data.left) + record_length(data.right)) / 5
    if user['credits'] <= tokens_needed:
        raise HTTPException(status_code=400, detail="Not enough credits.")
    
    # set config
    if data.config:
        libem.calibrate(data.config)
    
    # call match
    with libem.trace as t:
        try:
            output = libem.match(data.left, data.right)
        except Exception as e:
            raise HTTPException(status_code=500, 
                                detail=str(e))
        
        # get token usage
        tokens_used = 0
        for span in t.get():
            if 'match' not in span:
                continue
            
            model_usage = span['match']['model_usage']
            tokens_used += model_usage['num_input_tokens'] + model_usage['num_output_tokens']
        
        # update user toekns
        cur = con.cursor()
        cur.execute("UPDATE users SET credits = %s WHERE id = %s", 
                    (user['credits'] - tokens_used, user['id']))
        con.commit()
        cur.close()
    
    # reset libem
    libem.reset()
    
    return {"response": output,
            "credits": {
                "used": tokens_used,
                "remaining": user['credits'] - tokens_used
                }
            }


@app.post('/runsql', include_in_schema=False)
async def run_sql(data: RunSql, user=Depends(manager)):
    ''' Run a SQL query. Requires a password. '''
    
    if data.password != os.getenv("SQL_PASSWORD"):
        raise HTTPException(status_code=422, 
                            detail='Password is not correct. Your attempt has been logged.')
    
    cur = con.cursor(dictionary=True)
    try:
        cur.execute(data.query)
        results = cur.fetchall()
        con.commit()
        cur.close()
    
        return results
    except mysql.connector.Error as err:
        cur.close()
        raise HTTPException(status_code=500, detail=str(err))


# run the API
if __name__ == '__main__':
    uvicorn.run("run:app", host="0.0.0.0", port=8080, proxy_headers=True, forwarded_allow_ips='*')
