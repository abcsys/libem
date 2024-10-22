import os
import json
import random
import pathlib
import sqlite3
import time
import uvicorn
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
    'Human': {'description': 'Regular user.'},
    'Model': {'description': 'Any use of computer algorithms or artificial intelligence.'},
}


#####################
# SQL DB
#####################

con = sqlite3.connect("results.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users("
            "id int NOT null PRIMARY KEY, "
            "name varchar(200), "
            "email varchar(200), "
            "avatar varchar(200), "
            "type varchar(20), "
            "seed int, "
            "matching int, "
            "benchmark varchar(50), "
            "timestamp float)")
cur.execute("CREATE TABLE IF NOT EXISTS matches("
            "id int NOT null, "
            "type varchar(20) Not null, "
            "entity_1 varchar(5000), "
            "entity_2 varchar(5000), "
            "pred int NOT null, "
            "label int NOT null)")
cur.execute("CREATE TABLE IF NOT EXISTS leaderboard("
            "id int NOT null, "
            "type varchar(20) NOT null, "
            "name varchar(100), "
            "benchmark varchar(50) NOT null, "
            "pairs int NOT null, "
            "tp int NOT null, "
            "fp int NOT null, "
            "tn int NOT null, "
            "fn int NOT null, "
            "score float NOT null, "
            "avg_time float NOT null)")

res = cur.execute("SELECT * FROM leaderboard WHERE name='Libem'")
if res.fetchone() is None:
    # add libem results to leaderboard
    cur.executemany("INSERT INTO leaderboard VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [(
                        0, "Model", "Libem", name, metadata[name]['size'], 
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
    existing = cur.execute("SELECT * FROM users WHERE id = ?",
              (sub,)).fetchall()
    if len(existing) == 0:
        cur.execute("INSERT INTO users(id, name, email, avatar) VALUES(?, ?, ?, ?)",
                    (sub, user['name'], user['email'], user['picture']))
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
A benchmarking tool for EM.
Libem Arena supports benchmarking both users (preferably through the frontend) and EM models (through the API).
'''

tags_metadata = [
    {
        "name": "Init",
        "description": "The entry point to the API."
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
    con = sqlite3.connect("results.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user = cur.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
    cur.close()
    
    if len(user) == 0:
        return None
    
    return dict(user[0])

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
        cur = con.cursor()
        user_count = cur.execute("SELECT COUNT(*) AS count FROM users").fetchall()[0]
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
        return RedirectResponse(f'{os.getenv("FRONTEND_URL")}/?auth={access_token}')
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
    access_token = register_user(user)
    
    return RedirectResponse(f'{os.getenv("FRONTEND_URL")}/?auth={access_token}')

@app.get("/init", tags=["Init"])
async def init(user=Depends(manager.optional), type: str = ''):
    ''' Return benchmark info and updates user type if given. '''
    
    if user:
        if type in user_types and user['type'] != type:
            cur = con.cursor()
            cur.execute("UPDATE users SET type = ?, seed = ?, matching = ? "
                        "WHERE id = ?", 
                        (type, random.randint(0, 0xffffffff), 0, user['id']))
            con.commit()
            cur.close()
        else:
            type = user['type']
        
        return JSONResponse({
            'auth': True,
            'id': user['id'],
            'name': user['name'],
            'type': type,
            'avatar': user['avatar'],
            'user_types': user_types,
            'benchmarks': metadata,
            })
    
    return JSONResponse({
        'auth': False,
        'user_types': user_types,
        'benchmarks': metadata,
    })

@app.get("/match", tags=["Model"])
async def match(benchmark: str, user=Depends(manager)):
    ''' Return all pairs from a benchmark. '''
    
    validate(benchmark)
    
    if not user['type']:
        raise HTTPException(status_code=403,
                            detail="User type not set. Call /init first to set the user type.")
    if user['type'] != 'Model':
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /match_one instead "
                                   "or call /init again with a different token.")
    # only allow one active matching request at once
    if user['matching'] == 1:
        raise HTTPException(status_code=403, 
                            detail="Sumbit the previous matching request first "
                                   "or call /init again to reset.")
    
    # shuffle all pairs
    random.seed(user['seed'])
    indices = random.sample(range(0, metadata[benchmark]['size']), metadata[benchmark]['size'])
    bm = benchmarks[benchmark]['benchmark']
    pairs = [{'left': bm[i]['left'], 'right': bm[i]['right']} for i in indices]
    
    # update user info
    cur = con.cursor()
    cur.execute("UPDATE users SET matching = ?, benchmark = ?, timestamp = ? "
                "WHERE id = ?", 
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
    
    if not user['type']:
        raise HTTPException(status_code=403,
                            detail="User type not set. Call /init first to set the user type.")
    if user['type'] != 'Model':
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /submit_one instead "
                                   "or call /init again with a different token.")
    
    if user['matching'] == 0:
        raise HTTPException(status_code=403, 
                            detail="Request a new benchmark with /match first.")
    
    # set matching to false
    cur = con.cursor()
    cur.execute("UPDATE users SET matching = ? "
                "WHERE id = ?", 
                (0, user['id']))
    con.commit()
    cur.close()
    
    # verify answers
    if len(data.answers) != metadata[benchmark]['size']:
        raise HTTPException(status_code=400, detail='Number of entries do not match.')
    
    # get shuffled order
    random.seed(user['seed'])
    indices = random.sample(range(0, metadata[benchmark]['size']), metadata[benchmark]['size'])
    
    tp, fp, tn, fn = 0, 0, 0, 0
    for i, index in enumerate(indices):
        pair = benchmarks[benchmark]['benchmark'][index]
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
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND id = ? AND type = ? AND name = ?",
                      (benchmark, user['id'], user['type'], data.display_name)).fetchall()
    
    # if leaderboard entry does not exist, create entry, otherwise update entry
    if len(lb_entry) == 0:
        cur.execute("INSERT INTO leaderboard(id, type, name, benchmark, pairs, tp, fp, tn, fn, score, avg_time) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (user['id'], user['type'], data.display_name, benchmark, 
                     len(data.answers), tp, fp, tn, fn, f1, avg_time))
    elif lb_entry[0]['score'] < f1:
        cur.execute("UPDATE leaderboard "
                    "SET pairs = ?, tp = ?, fp = ?, tn = ?, fn = ?, score = ?, avg_time = ? "
                    "WHERE id = ? AND benchmark = ? AND name = ?", 
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
    
    if not user['type']:
        raise HTTPException(status_code=403,
                            detail="User type not set. Call /init first to set the user type.")
    
    # get current number of pairs matched from leaderboard
    cur = con.cursor()
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND id = ? AND type = ?",
                      (benchmark, user['id'], user['type'])).fetchall()
    cur.close()
    
    # get the last matched pair
    if len(lb_entry) == 0:
        lb_entry = {}
    else:
        lb_entry = dict(lb_entry[0])
    pairs = lb_entry.get('pairs', 0)
    
    # if no more pairs, return error
    if pairs >= metadata[benchmark]['size']:
        raise HTTPException(status_code=204, detail='End of benchmark.')
    
    # sample the next pair
    random.seed(user['seed'])
    index = random.sample(range(0, metadata[benchmark]['size']), pairs + 1)[-1]
    pair = benchmarks[benchmark]['benchmark'][index]
    
    # update user info
    cur = con.cursor()
    cur.execute("UPDATE users SET matching = ?, benchmark = ?, timestamp = ? "
                "WHERE id = ?", 
                (1, benchmark, time.time(), user['id']))
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
    
    if not user['type']:
        raise HTTPException(status_code=403,
                            detail="User type not set. Call /init first to set the user type.")
    
    if user['matching'] == 0:
        raise HTTPException(status_code=403, 
                            detail="Request a new pair with /matchone first.")
    
    # get current leaderboard entry
    cur = con.cursor()
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND id = ? AND type = ?",
                      (data.benchmark, user['id'], user['type'])).fetchall()
    cur.close()
    
    # get the last matched pair
    if len(lb_entry) == 0:
        lb_entry = {}
    else:
        lb_entry = dict(lb_entry[0])
    pairs = lb_entry.get('pairs', 0)
        
    random.seed(user['seed'])
    index = random.sample(range(0, metadata[data.benchmark]['size']), pairs + 1)[-1]
    pair = benchmarks[data.benchmark]['benchmark'][index]
    
    # add submission to matches db and update user info
    cur = con.cursor()
    cur.execute("INSERT INTO matches VALUES(?, ?, ?, ?, ?, ?)", (
        user['id'], user['type'], json.dumps(pair['left']), json.dumps(pair['right']), 
        data.answer, pair['label']))
    cur.execute("UPDATE users SET matching = ? "
                "WHERE id = ?", 
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
    if data.time is not None and data.time > 0 and time_taken - 5 <= data.time <= time_taken:
        time_taken = data.time
    
    # if leaderboard entry does not exist, create entry, otherwise update entry
    if len(lb_entry) == 0:
        cur.execute("INSERT INTO leaderboard(id, type, benchmark, pairs, tp, fp, tn, fn, score, avg_time) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (user['id'], user['type'], data.benchmark, 1, tp, fp, tn, fn, f1, time_taken))
    else:
        avg_time = (lb_entry['avg_time'] * pairs + time_taken) / (pairs + 1)
        cur.execute("UPDATE leaderboard "
                    "SET pairs = ?, tp = ?, fp = ?, tn = ?, fn = ?, score = ?, avg_time = ? "
                    "WHERE id = ? AND benchmark = ?", 
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
    cur = con.cursor()
    
    model_lb = cur.execute("SELECT * FROM leaderboard WHERE benchmark = ? AND type = ? ORDER BY score DESC",
                           (benchmark, 'Model')).fetchall()
    human_best = cur.execute(f"SELECT '1' as id, 'Users Best' as name, '{benchmark}' as benchmark, "
                       "COALESCE(MAX(pairs), 0) as pairs, COALESCE(MAX(score), 0) as score, "
                       "COALESCE(MAX(avg_time), 0) as avg_time "
                       "FROM leaderboard WHERE benchmark = ? AND type = ? ORDER BY score DESC LIMIT 1", 
                       (benchmark, "Human")).fetchall()
    human_avg = cur.execute(f"SELECT '2' as id, 'Users Avg' as name, '{benchmark}' as benchmark, "
                      "COALESCE(AVG(pairs), 0) as pairs, COALESCE(AVG(score), 0) as score, "
                      "COALESCE(AVG(avg_time), 0) as avg_time "
                      "FROM leaderboard WHERE benchmark = ? AND type = ?",
                      (benchmark, "Human")).fetchall()
    if user is not None and user['type'] == 'Human':
        human = cur.execute("SELECT * FROM leaderboard WHERE benchmark = ? AND id = ? AND type = ?",
                            (benchmark, user['id'], "Human")).fetchall()
    
    cur.close()
    
    filtered_lb = [dict(m) for m in model_lb]
    filtered_lb.extend([dict(human_best[0]), dict(human_avg[0])])
    if user is not None and user['type'] == 'Human':
        filtered_lb.extend([dict(u) for u in human])
    return sorted(filtered_lb, key=cmp_to_key(compare), reverse=True)

@app.post('/deleteuser', tags=["Misc"])
async def delete_user(user=Depends(manager)):
    ''' Delete the current user from the database. '''
    
    cur = con.cursor()
    for table in ['users', 'matches', 'leaderboard']:
        cur.execute(f"DELETE FROM {table} WHERE id = ?",
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
    output = cur.execute(data.query).fetchall()
    results = [dict(i) for i in output]
    con.commit()
    cur.close()
    
    return results

# run the API
if __name__ == "__main__":
        uvicorn.run("serve:app", host=os.getenv('BACKEND_HOST'), 
                                 port=int(os.getenv('BACKEND_PORT')), 
                                 proxy_headers=True, 
                                 forwarded_allow_ips='*')
