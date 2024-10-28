import os
import json
import random
import pathlib
import time
import uvicorn
import mysql.connector
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_login import LoginManager
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from pydantic import BaseModel
from functools import cmp_to_key

import libem.prepare.datasets as ds
from libem.prepare.datasets import (abt_buy, amazon_google, beer, dblp_acm, 
                                    dblp_scholar, fodors_zagats, itunes_amazon, 
                                    walmart_amazon, challenging)

# load .env if needed
if not os.getenv('SECRET'):
    from dotenv import load_dotenv
    env_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), 'arena.env')
    load_dotenv(env_path)

#####################
# POST structs
#####################

class Submit(BaseModel):
    answers: list[bool | int]
    display_name: str
class SubmitOne(BaseModel):
    benchmark: str
    answer: bool
    time: float | None = None
    display_name: str | None = None
class RunSql(BaseModel):
    query: str
    password: str


#####################
# Benchmarks
#####################

def read_demo(ds_name):
    ds_name = ds_name.lower()
    path = os.path.join(ds.LIBEM_SAMPLE_DATA_PATH, ds_name)
    demo_file = os.path.join(os.path.join(path, 'demo'), 'demo.ndjson')
    with open(demo_file, 'r') as f:
        benchmark = []
        for line in f:
            benchmark.append(json.loads(line))
        return benchmark

def read_result(ds_name):
    ds_name = ds_name.lower()
    results_folder = os.path.join(os.path.join(ds.LIBEM_SAMPLE_DATA_PATH, 'libem-results'), 'demo')
    file = os.path.join(results_folder, f'{ds_name}.json')
    with open(file, 'r') as f:
        return json.load(f)

benchmark_list = {
    'Abt-Buy': abt_buy,
    'Amazon-Google': amazon_google,
    'Beer': beer,
    'DBLP-ACM': dblp_acm,
    'DBLP-Scholar': dblp_scholar,
    'Fodors-Zagats': fodors_zagats,
    'Itunes-Amazon': itunes_amazon,
    'Walmart-Amazon': walmart_amazon,
    'Challenging': challenging,
}
benchmarks = {
    name: {
        'description': d.description,
        'benchmark': read_demo(name)
    }
    for name, d in benchmark_list.items()
}
metadata = {
    name: {
            'description': v['description'],
            'size': len(v['benchmark'])
    }
    for name, v in benchmarks.items()
}

libem_results = {
    name: read_result(name) for name in benchmark_list.keys()
}

user_types = {
    'h': 'human',
    'm': 'model',
}


#####################
# SQL DB
#####################

def connect_sql():
    return mysql.connector.connect(user='mysql', password='password',
                                   host=os.getenv('MYSQL_IP'),
                                   database='arenadb')

con = connect_sql()
cur = con.cursor(dictionary=True)
cur.execute("CREATE TABLE IF NOT EXISTS users("
            "id varchar(30) NOT null PRIMARY KEY, "
            "name varchar(200), "
            "email varchar(200), "
            "avatar varchar(200), "
            "seed int, "
            "matching int, "
            "benchmark varchar(50), "
            "timestamp double)")
cur.execute("CREATE TABLE IF NOT EXISTS matches("
            "id varchar(30) NOT null, "
            "type varchar(20) Not null, "
            "entity_1 varchar(5000), "
            "entity_2 varchar(5000), "
            "pred int NOT null, "
            "label int NOT null)")
cur.execute("CREATE TABLE IF NOT EXISTS leaderboard("
            "id varchar(30) NOT null, "
            "type varchar(20) NOT null, "
            "name varchar(100), "
            "benchmark varchar(50) NOT null, "
            "pairs int NOT null, "
            "tp int NOT null, "
            "fp int NOT null, "
            "tn int NOT null, "
            "fn int NOT null, "
            "score float NOT null, "
            "avg_time double NOT null)")

cur.execute("SELECT * FROM leaderboard WHERE name='Libem'")
res = cur.fetchall()
if not res:
    # add libem results to leaderboard
    cur.executemany("INSERT INTO leaderboard VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [(
                        0, "model", "Libem", name, metadata[name]['size'], 
                        libem_results[name]['stats']['confusion_matrix']['tp'], 
                        libem_results[name]['stats']['confusion_matrix']['fp'], 
                        libem_results[name]['stats']['confusion_matrix']['tn'], 
                        libem_results[name]['stats']['confusion_matrix']['fn'], 
                        libem_results[name]['stats']['f1'], 
                        round(libem_results[name]['stats']['latency'] / metadata[name]['size'], 3))
                    for name in benchmark_list.keys()])
    con.commit()
cur.close()


#####################
# OAuth
#####################

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
# Helper methods
#####################

def compare(a, b):
    ''' Compare function for ordering leaderboard entries. '''
    return a['score'] - b['score']

def validate(benchmark: str):
    ''' Check validity of benchmark. '''
    
    if benchmark not in benchmark_list.keys():
        raise HTTPException(status_code=422, detail='Benchmark not found.')

def register_user(user: dict):
    sub = user['sub']
    
    # add user to db
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (sub,))
    existing = cur.fetchall()
    if len(existing) == 0:
        cur.execute("INSERT INTO users(id, name, email, avatar, seed, matching) VALUES(%s, %s, %s, %s, %s, %s)",
                    (sub, user['name'], user['email'], user['picture'], random.randint(0, 0xfffffff), 0))
        con.commit()
    cur.close()
    
    # generate access tokens
    user_token = manager.create_access_token(
        data=dict(sub=f'{sub}h'),
        expires=timedelta(days=30)
    )
    model_token = manager.create_access_token(
        data=dict(sub=f'{sub}m'),
        expires=timedelta(days=30)
    )
    
    return user_token, model_token


#####################
# FastAPI
#####################

description = '''
A benchmarking tool for EM.
Libem Arena supports benchmarking both users (preferably through the frontend) and EM models (through the API).
'''

tags_metadata = [
    {
        "name": "Init",
        "description": "The entry points to the API."
    },
    {
        "name": "Model Only",
        "description": "The API for benchmarking EM models. "
                       "All entries of a benchmark will be provided in a single call to /match "
                       "and all answers need to be submitted in the same call to /submit."
    },
    {
        "name": "User/Model",
        "description": "The API for benchmarking users and is integrated with the Libem Arena frontend. "
                       "Each entry of a benchmark will be provided one at a time with each call to /matchone "
                       "and answers are submitted one at a time to /submitone."
    },
    {
        "name": "Misc",
        "description": "Miscellaneous calls that interact with the database."
    },
]

app = FastAPI(
    root_path=os.getenv('BACKEND_ROOT_PATH', ''),
    openapi_prefix=os.getenv('BACKEND_ROOT_PATH', ''),
    title="Libem Arena API",
    description=description,
    openapi_tags=tags_metadata,
)

app.add_middleware(SessionMiddleware, secret_key=SECRET)

# handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL')],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# fetch user data once authenticated
@manager.user_loader()
def load_user(user_id: str):
    # separate user type identifier
    sub = user_id[:-1]
    user_type = user_id[-1]
    
    con = connect_sql()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id = %s", (sub,))
    user = cur.fetchall()
    cur.close()
    
    if len(user) == 0 or user_type not in user_types:
        return None
    
    user = user[0]
    user['type'] = user_types[user_id[-1]]
    
    return user

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    return JSONResponse(
        status_code=401,
        content="Authentication token expired or invalid. "
                "Try logging in again from your browser at "
                "https://arena.libem.org."
    )
    
@app.get("/login", tags=["Init"])
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
        
        user_token, model_token = register_user(user)
        return RedirectResponse(f'{os.getenv("FRONTEND_URL")}/?auth={user_token}&token={model_token}')
    else:
        # absolute url for callback
        redirect_uri = request.url_for('auth')
        return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth", include_in_schema=False)
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return RedirectResponse(os.getenv('FRONTEND_URL'))
    
    user = token.get('userinfo')
    user_token, model_token = register_user(user)
    
    return RedirectResponse(f'{os.getenv("FRONTEND_URL")}/?auth={user_token}&token={model_token}')

@app.get("/info", tags=["Init"])
async def info(user=Depends(manager.optional)):
    ''' Return user info and available benchmarks. '''
    
    if user:
        return JSONResponse({
            'auth': True,
            'id': user['id'],
            'name': user['name'],
            'type': user['type'],
            'avatar': user['avatar'],
            'benchmarks': metadata,
            })
    else:
        return JSONResponse({
            'auth': False,
            'benchmarks': metadata,
        })

@app.get("/match", tags=["Model"])
async def match(benchmark: str, user=Depends(manager)):
    ''' Return all pairs from a benchmark. '''
    
    validate(benchmark)
    
    if user['type'] != 'model':
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /match_one instead "
                                   "or call /init again with a different token.")
    # only allow one active matching request at once
    if user['matching'] == 1:
        raise HTTPException(status_code=403, 
                            detail="Sumbit the previous matching request first "
                                   "or call /init again to reset.")
    
    pairs = [{'left': bm['left'], 'right': bm['right']} for bm in benchmarks[benchmark]['benchmark']]
    
    # update user info
    cur = con.cursor()
    cur.execute("UPDATE users SET matching = %s, benchmark = %s, timestamp = %s "
                "WHERE id = %s", 
                (1, benchmark, time.time(), user['id']))
    con.commit()
    cur.close()
    
    return {
        'benchmark': metadata[benchmark],
        'pairs': pairs
    }

@app.post("/submit", tags=["Model"])
async def submit(data: Submit, user=Depends(manager)):
    ''' Save all answers and return stats. '''
    
    submit_time = time.time()
    benchmark = user['benchmark']
    
    if user['type'] != 'model':
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /submit_one instead "
                                   "or call /init again with a different token.")
    
    if user['matching'] == 0:
        raise HTTPException(status_code=403, 
                            detail="Request a new benchmark with /match first.")
    
    # set matching to false
    cur = con.cursor()
    cur.execute("UPDATE users SET matching = %s "
                "WHERE id = %s", 
                (0, user['id']))
    con.commit()
    cur.close()
    
    # verify answers
    if len(data.answers) != metadata[benchmark]['size']:
        raise HTTPException(status_code=400, detail='Number of entries do not match.')
    
    tp, fp, tn, fn = 0, 0, 0, 0
    for i, pair in enumerate(benchmarks[benchmark]['benchmark']):
        answer = data.answers[i]
        
        if pair['label'] == 1:
            if int(answer) == 1:
                tp += 1
            else:
                fn += 1
        else:
            if int(answer) == 1:
                fp += 1
            else:
                tn += 1
    
    f1 = 100 if tp + fp + fn == 0 else tp / (tp + .5 * (fp + fn)) * 100

    time_taken = submit_time - user['timestamp']
    avg_time = time_taken / len(data.answers)
    
    cur = con.cursor()
    
    # get current leaderboard entry
    cur.execute("SELECT * FROM leaderboard "
                "WHERE benchmark = %s AND id = %s AND type = %s AND name = %s",
                (benchmark, user['id'], user['type'], data.display_name))
    lb_entry = cur.fetchall()
    
    # if leaderboard entry does not exist, create entry, otherwise update entry
    if len(lb_entry) == 0:
        cur.execute("INSERT INTO leaderboard(id, type, name, benchmark, pairs, tp, fp, tn, fn, score, avg_time) "
                    "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    (user['id'], user['type'], data.display_name, benchmark, 
                     len(data.answers), tp, fp, tn, fn, f1, avg_time))
    elif lb_entry[0]['score'] < f1:
        cur.execute("UPDATE leaderboard "
                    "SET pairs = %s, tp = %s, fp = %s, tn = %s, fn = %s, score = %s, avg_time = %s "
                    "WHERE id = %s AND benchmark = %s AND name = %s", 
                    (len(data.answers), tp, fp, tn, fn, f1, avg_time, user['id'], benchmark, data.display_name))
        
    con.commit()
    cur.close()
    
    return {
        'benchmark': metadata[benchmark],
        'score': f1,
        'time': time_taken
    }

@app.get("/matchone", tags=["User"])
async def match_one(benchmark: str, user=Depends(manager)):
    ''' Return the next pair from a benchmark. '''
    
    validate(benchmark)
    
    # get current number of pairs matched from leaderboard
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM leaderboard "
                "WHERE benchmark = %s AND id = %s AND type = %s",
                (benchmark, user['id'], user['type']))
    lb_entry = cur.fetchall()
    cur.close()
    
    # get the last matched pair
    if len(lb_entry) == 0:
        lb_entry = {}
    else:
        lb_entry = lb_entry[0]
    pairs = lb_entry.get('pairs', 0)
    
    # if no more pairs, return error
    if pairs >= metadata[benchmark]['size']:
        raise HTTPException(status_code=204, detail='End of benchmark.')
    
    # sample the next pair
    random.seed(user['seed'])
    index = random.sample(range(0, metadata[benchmark]['size']), pairs + 1)[-1]
    pair = benchmarks[benchmark]['benchmark'][index]
    timestamp = time.time()
    
    # update user info
    cur = con.cursor()
    cur.execute("UPDATE users SET matching = %s, benchmark = %s, timestamp = %s "
                "WHERE id = %s", 
                (1, benchmark, timestamp, user['id']))
    con.commit()
    cur.close()
    
    return {
        'index': pairs,
        'left': pair['left'],
        'right': pair['right']
    }

@app.post("/submitone", tags=["User"])
async def submit_one(data: SubmitOne, user=Depends(manager)):
    ''' Save the answer and return the label. '''
    
    submit_time = time.time()
    
    if user['matching'] == 0:
        raise HTTPException(status_code=403, 
                            detail="Request a new pair with /matchone first.")
    
    # get current leaderboard entry
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM leaderboard "
                "WHERE benchmark = %s AND id = %s AND type = %s",
                (data.benchmark, user['id'], user['type']))
    lb_entry = cur.fetchall()
    cur.close()
    
    # get the last matched pair
    if len(lb_entry) == 0:
        lb_entry = {}
    else:
        lb_entry = lb_entry[0]
    pairs = lb_entry.get('pairs', 0)
        
    random.seed(user['seed'])
    index = random.sample(range(0, metadata[data.benchmark]['size']), pairs + 1)[-1]
    pair = benchmarks[data.benchmark]['benchmark'][index]
    
    # add submission to matches db and update user info
    cur = con.cursor()
    cur.execute("INSERT INTO matches VALUES(%s, %s, %s, %s, %s, %s)", (
        user['id'], user['type'], json.dumps(pair['left']), json.dumps(pair['right']), 
        data.answer, pair['label']))
    cur.execute("UPDATE users SET matching = %s "
                "WHERE id = %s", 
                (0, user['id']))
    
    # verify answer
    tp, fp = lb_entry.get('tp', 0), lb_entry.get('fp', 0), 
    tn, fn = lb_entry.get('tn', 0), lb_entry.get('fn', 0)
    if pair['label'] == 1:
        if int(data.answer) == 1:
            tp += 1
        else:
            fn += 1
    else:
        if int(data.answer) == 1:
            fp += 1
        else:
            tn += 1
    f1 = 100 if tp + fp + fn == 0 else tp / (tp + .5 * (fp + fn)) * 100
    
    # verify reported time is close to server-tracked time
    time_taken = submit_time - user['timestamp']
    if data.time is not None and time_taken - 2 <= data.time <= time_taken + 2 or time_taken < 0:
        time_taken = data.time
    
    # if leaderboard entry does not exist, create entry, otherwise update entry
    if len(lb_entry) == 0:
        cur.execute("INSERT INTO leaderboard(id, type, name, benchmark, pairs, tp, fp, tn, fn, score, avg_time) "
                    "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    (user['id'], user['type'], data.display_name, data.benchmark, 1, tp, fp, tn, fn, f1, time_taken))
    else:
        avg_time = (lb_entry['avg_time'] * pairs + time_taken) / (pairs + 1)
        cur.execute("UPDATE leaderboard "
                    "SET pairs = %s, tp = %s, fp = %s, tn = %s, fn = %s, score = %s, avg_time = %s "
                    "WHERE id = %s AND benchmark = %s", 
                    (pairs + 1, tp, fp, tn, fn, f1, avg_time, user['id'], data.benchmark))
    
    con.commit()
    cur.close()
    
    libem_res = libem_results[data.benchmark]['results'][index]
    
    return {
        'label': pair['label'],
        'libem_time': libem_res['latency'],
        'libem_pred': libem_res['pred'] == 'yes'
    }

@app.get("/leaderboard", tags=["Misc"])
async def get_leaderboard(benchmark: str, user=Depends(manager.optional)):
    ''' Get the leaderboard for a benchmark. '''
    
    validate(benchmark)
    cur = con.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM leaderboard WHERE benchmark = %s AND type = %s ORDER BY score DESC",
                           (benchmark, 'model'))
    model_lb = cur.fetchall()
    cur.execute(f"SELECT '-1' as id, 'Users Best' as name, '{benchmark}' as benchmark, "
                       "COALESCE(MAX(pairs), 0) as pairs, COALESCE(MAX(score), 0) as score, "
                       "COALESCE(MAX(avg_time), 0) as avg_time "
                       "FROM leaderboard WHERE benchmark = %s AND type = %s ORDER BY score DESC LIMIT 1", 
                       (benchmark, "human"))
    human_best = cur.fetchall()
    cur.execute(f"SELECT '-2' as id, 'Users Avg' as name, '{benchmark}' as benchmark, "
                      "COALESCE(AVG(pairs), 0) as pairs, COALESCE(AVG(score), 0) as score, "
                      "COALESCE(AVG(avg_time), 0) as avg_time "
                      "FROM leaderboard WHERE benchmark = %s AND type = %s",
                      (benchmark, "human"))
    human_avg = cur.fetchall()
    if user is not None and user['type'] == 'human':
        cur.execute("SELECT * FROM leaderboard WHERE benchmark = %s AND id = %s AND type = %s",
                            (benchmark, user['id'], "human"))
        human = cur.fetchall()
    
    cur.close()
    
    filtered_lb = model_lb
    filtered_lb.extend([human_best[0], human_avg[0]])
    if user is not None and user['type'] == 'human':
        filtered_lb.extend(human)
    return sorted(filtered_lb, key=cmp_to_key(compare), reverse=True)

@app.post('/deleteuser', tags=["Misc"])
async def delete_user(user=Depends(manager)):
    ''' Delete the current user from the database. '''
    
    cur = con.cursor()
    for table in ['users', 'matches', 'leaderboard']:
        cur.execute(f"DELETE FROM {table} WHERE id = %s",
                    (user['id'],))
    con.commit()
    cur.close()

@app.post('/runsql', include_in_schema=False)
async def run_sql(data: RunSql, user=Depends(manager)):
    ''' Run a SQL query. Requires a password. '''
    
    if data.password != os.getenv('SQL_PASSWORD'):
        raise HTTPException(status_code=422, 
                            detail='Password is not correct. Your attempt has been logged.')
    
    cur = con.cursor()
    try:
        cur.execute(data.query)
        output = cur.fetchall()
        results = output
        con.commit()
        cur.close()
        
        return results
    except mysql.connector.Error as err:
        cur.close()
        raise HTTPException(status_code=500, detail=str(err))

# run the API
if __name__ == "__main__":
        uvicorn.run("serve:app", host=os.getenv('BACKEND_HOST'), 
                                 port=int(os.getenv('BACKEND_PORT')), 
                                 proxy_headers=True, 
                                 forwarded_allow_ips='*')
