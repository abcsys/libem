import os
import json
import random
import hashlib
import sqlite3
import time
import uvicorn
import uuid as uuidlib
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from functools import cmp_to_key

import libem.prepare.datasets as ds
from libem.prepare.datasets import (abt_buy, amazon_google, beer, dblp_acm, 
                                    dblp_scholar, fodors_zagats, itunes_amazon, 
                                    walmart_amazon, challenging)


#####################
# POST structs
#####################

class Submit(BaseModel):
    uuid: str
    answers: list[bool | int]
    display_name: str
class SubmitOne(BaseModel):
    uuid: str
    benchmark: str
    answer: bool
    time: float | None = None
class DeleteUser(BaseModel):
    uuid: str
    password: str | None = None
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

# read in secrets
home_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(os.path.join(home_dir, 'secrets'), 'secrets.json'), 'r') as f:
    secrets = json.load(f)


#####################
# SQL DB
#####################

con = sqlite3.connect("results.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS sessions("
            "uuid char(36) NOT null PRIMARY KEY, "
            "type varchar(20) NOT null, "
            "seed int NOT null, "
            "matching int, "
            "benchmark varchar(50), "
            "timestamp float)")
cur.execute("CREATE TABLE IF NOT EXISTS matches("
            "uuid char(36) NOT null, "
            "type varchar(20) Not null, "
            "entity_1 varchar(5000), "
            "entity_2 varchar(5000), "
            "pred int NOT null, "
            "label int NOT null)")
cur.execute("CREATE TABLE IF NOT EXISTS leaderboard("
            "uuid char(36) NOT null, "
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
                        "0", "model", "Libem", name, metadata[name]['size'], 
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
# Helper methods
#####################

def compare(a, b):
    ''' Compare function for ordering leaderboard entries. '''
    return a['score'] - b['score']

def validate(uuid: str, benchmark: str = None):
    ''' Check validity of uuid and optionally benchmark. '''
    
    try:
        uuid = str(uuidlib.UUID(uuid))
    except ValueError:
        raise HTTPException(status_code=422, 
                            detail='UUID is not valid. '
                                   'Call /init to get a valid UUID first.')
    
    if benchmark is not None and benchmark not in benchmark_list.keys():
        raise HTTPException(status_code=422, detail='Benchmark not found.')
    
    return uuid

def get_session(uuid: str):
    ''' Get session info for uuid. '''
    
    cur = con.cursor()
    session = cur.execute("SELECT * FROM sessions WHERE uuid = ?",
              (uuid,)).fetchall()
    cur.close()
    
    if len(session) == 0:
        raise HTTPException(status_code=400, 
                            detail='UUID does not exist. '
                                   'Call /init with your UUID first.')
    
    return dict(session[0])


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
        "description": "The entry point to the API. Returns a UUID and a list of available benchmarks."
    },
    {
        "name": "Model",
        "description": "The API for benchmarking EM models. "
                       "All entries of a benchmark will be provided in a single call to /match "
                       "and all answers need to be submitted in the same call to /submit."
    },
    {
        "name": "User",
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
    title="Libem Arena API",
    description=description,
    openapi_tags=tags_metadata
)

# handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/init/", tags=["Init"])
async def init(request: Request, token: str = '', uuid: str = ''):
    ''' Return benchmark info and generates a UUID if not given. '''

    # check if provided uuid and token are valid
    try:
        uuid = str(uuidlib.UUID(uuid))
    except ValueError:
        # if not, try to generate a new uuid from the request header
        if request.headers:
            hash_str = str(request.headers)
        else:
            hash_str = str(uuidlib.uuid4())
        hex = hashlib.md5(hash_str.encode("UTF-8")).hexdigest()
        uuid = str(uuidlib.UUID(hex=hex))
    if token not in secrets['tokens'].keys():
        raise HTTPException(status_code=422, detail='Bad token.')

    # add to sessions db if not exists, or update token
    cur = con.cursor()
    session = cur.execute("SELECT seed FROM sessions WHERE uuid = ?",
              (uuid,)).fetchall()
    if len(session) == 0:
        cur.execute("INSERT INTO sessions(uuid, type, seed) VALUES(?, ?, ?)", 
                    (uuid, secrets['tokens'][token], random.randint(0, 0xffffffff)))
    else:
        cur.execute("UPDATE sessions SET type = ?, seed = ?, matching = ? "
                    "WHERE uuid = ?", 
                    (secrets['tokens'][token], dict(session[0])['seed'], 0, uuid))
    con.commit()
    cur.close()
    
    return {
        'uuid': uuid,
        'benchmarks': metadata
    }

@app.get("/match/", tags=["Model"])
async def match(uuid: str, benchmark: str):
    ''' Return all pairs from a benchmark. '''
    
    uuid = validate(uuid, benchmark)
    session = get_session(uuid)
    
    if session['type'] in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /match_one instead "
                                   "or call /init again with a different token.")
    # only allow one active matching request at once
    if session['matching'] == 1:
        raise HTTPException(status_code=403, 
                            detail="Sumbit the previous matching request first "
                                   "or call /init again to reset.")
    
    # shuffle all pairs
    random.seed(session['seed'])
    indices = random.sample(range(0, metadata[benchmark]['size']), metadata[benchmark]['size'])
    bm = benchmarks[benchmark]['benchmark']
    pairs = [{'left': bm[i]['left'], 'right': bm[i]['right']} for i in indices]
    
    # update session info
    cur = con.cursor()
    cur.execute("UPDATE sessions SET matching = ?, benchmark = ?, timestamp = ? "
                "WHERE uuid = ?", 
                (1, benchmark, time.time(), uuid))
    con.commit()
    cur.close()
    
    return {
        'uuid': uuid,
        'benchmark': metadata[benchmark],
        'pairs': pairs
    }

@app.post("/submit/", tags=["Model"])
async def submit(data: Submit):
    ''' Save all answers and return stats. '''
    
    submit_time = time.time()
    
    uuid = validate(data.uuid)
    session = get_session(uuid)
    benchmark = session['benchmark']
    
    if session['type'] in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /submit_one instead "
                                   "or call /init again with a different token.")
    
    if session['matching'] == 0:
        raise HTTPException(status_code=403, 
                            detail="Request a new benchmark with /match first.")
    
    # set matching to false
    cur = con.cursor()
    cur.execute("UPDATE sessions SET matching = ? "
                "WHERE uuid = ?", 
                (0, uuid))
    con.commit()
    cur.close()
    
    # verify answers
    if len(data.answers) != metadata[benchmark]['size']:
        raise HTTPException(status_code=400, detail='Number of entries do not match.')
    
    # get shuffled order
    random.seed(session['seed'])
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

    time_taken = submit_time - session['timestamp']
    avg_time = time_taken / len(data.answers)
    
    cur = con.cursor()
    
    # get current leaderboard entry
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND uuid = ? AND type = ? AND name = ?",
                      (benchmark, uuid, session['type'], data.display_name)).fetchall()
    
    # if leaderboard entry does not exist, create entry, otherwise update entry
    if len(lb_entry) == 0:
        cur.execute("INSERT INTO leaderboard(uuid, type, name, benchmark, pairs, tp, fp, tn, fn, score, avg_time) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (uuid, session['type'], data.display_name, benchmark, 
                     len(data.answers), tp, fp, tn, fn, f1, avg_time))
    elif lb_entry[0]['score'] < f1:
        cur.execute("UPDATE leaderboard "
                    "SET pairs = ?, tp = ?, fp = ?, tn = ?, fn = ?, score = ?, avg_time = ? "
                    "WHERE uuid = ? AND benchmark = ? AND name = ?", 
                    (len(data.answers), tp, fp, tn, fn, f1, avg_time, uuid, benchmark, data.display_name))
        
    con.commit()
    cur.close()
    
    return {
        'uuid': uuid,
        'benchmark': metadata[benchmark],
        'score': f1,
        'time': time_taken
    }

@app.get("/matchone/", tags=["User"])
async def match_one(uuid: str, benchmark: str):
    ''' Return the next pair from a benchmark. '''
    
    uuid = validate(uuid, benchmark)
    session = get_session(uuid)
    
    if session['type'] not in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /match instead "
                                   "or call /init again with a different token.")
    
    # get current number of pairs matched from leaderboard
    cur = con.cursor()
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND uuid = ? AND type = ?",
                      (benchmark, uuid, session['type'])).fetchall()
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
    random.seed(session['seed'])
    index = random.sample(range(0, metadata[benchmark]['size']), pairs + 1)[-1]
    pair = benchmarks[benchmark]['benchmark'][index]
    
    # update session info
    cur = con.cursor()
    cur.execute("UPDATE sessions SET matching = ?, benchmark = ?, timestamp = ? "
                "WHERE uuid = ?", 
                (1, benchmark, time.time(), uuid))
    con.commit()
    cur.close()
    
    return {
        'index': pairs,
        'left': pair['left'],
        'right': pair['right']
    }

@app.post("/submitone/", tags=["User"])
async def submit_one(data: SubmitOne):
    ''' Save the answer and return the label. '''
    
    submit_time = time.time()
    
    uuid = validate(data.uuid)
    session = get_session(uuid)
    
    if session['type'] not in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /submit instead "
                                   "or call /init again with a different token.")
    
    if session['matching'] == 0:
        raise HTTPException(status_code=403, 
                            detail="Request a new pair with /matchone first.")
    
    # get current leaderboard entry
    cur = con.cursor()
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND uuid = ? AND type = ?",
                      (data.benchmark, uuid, session['type'])).fetchall()
    cur.close()
    
    # get the last matched pair
    if len(lb_entry) == 0:
        lb_entry = {}
    else:
        lb_entry = dict(lb_entry[0])
    pairs = lb_entry.get('pairs', 0)
        
    random.seed(session['seed'])
    index = random.sample(range(0, metadata[data.benchmark]['size']), pairs + 1)[-1]
    pair = benchmarks[data.benchmark]['benchmark'][index]
    
    # add submission to matches db and update session info
    cur = con.cursor()
    cur.execute("INSERT INTO matches VALUES(?, ?, ?, ?, ?, ?)", (
        data.uuid, session['type'], json.dumps(pair['left']), json.dumps(pair['right']), 
        data.answer, pair['label']))
    cur.execute("UPDATE sessions SET matching = ? "
                "WHERE uuid = ?", 
                (0, uuid))
    
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
    time_taken = submit_time - session['timestamp']
    if data.time is not None and time_taken - 2 <= data.time <= time_taken:
        time_taken = data.time
    
    # if leaderboard entry does not exist, create entry, otherwise update entry
    if len(lb_entry) == 0:
        cur.execute("INSERT INTO leaderboard(uuid, type, benchmark, pairs, tp, fp, tn, fn, score, avg_time) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (uuid, session['type'], data.benchmark, 1, tp, fp, tn, fn, f1, time_taken))
    else:
        avg_time = (lb_entry['avg_time'] * pairs + time_taken) / (pairs + 1)
        cur.execute("UPDATE leaderboard "
                    "SET pairs = ?, tp = ?, fp = ?, tn = ?, fn = ?, score = ?, avg_time = ? "
                    "WHERE uuid = ? AND benchmark = ?", 
                    (pairs + 1, tp, fp, tn, fn, f1, avg_time, uuid, data.benchmark))
    
    con.commit()
    cur.close()
    
    libem_res = libem_results[data.benchmark]['results'][index]
    
    return {
        'label': pair['label'],
        'libem_time': libem_res['latency'],
        'libem_pred': libem_res['pred'] == 'yes'
    }

@app.get("/leaderboard/", tags=["Misc"])
async def get_leaderboard(benchmark: str, uuid: str | None = None):
    ''' Get the leaderboard for a benchmark, optionally pass in a UUID to get its entries. '''
    
    if uuid is not None:
        uuid = validate(uuid)
        session = get_session(uuid)
    
    cur = con.cursor()
    
    libem = cur.execute("SELECT * FROM leaderboard WHERE benchmark = ? AND uuid = ? LIMIT 1", 
                        (benchmark, "0")).fetchall()
    best = cur.execute(f"SELECT '1' as uuid, 'Users Best' as name, '{benchmark}' as benchmark, "
                       "COALESCE(MAX(pairs), 0) as pairs, COALESCE(MAX(score), 0) as score, "
                       "COALESCE(MAX(avg_time), 0) as avg_time "
                       "FROM leaderboard WHERE benchmark = ? AND type = ? ORDER BY score DESC LIMIT 1", 
                       (benchmark, "user")).fetchall()
    avg = cur.execute(f"SELECT '2' as uuid, 'Users Avg' as name, '{benchmark}' as benchmark, "
                      "COALESCE(AVG(pairs), 0) as pairs, COALESCE(AVG(score), 0) as score, "
                      "COALESCE(AVG(avg_time), 0) as avg_time "
                      "FROM leaderboard WHERE benchmark = ? AND type = ?",
                      (benchmark, "user")).fetchall()
    if uuid is not None:
        user = cur.execute("SELECT * FROM leaderboard WHERE benchmark = ? AND uuid = ? AND type = ?",
                           (benchmark, uuid, session['type'])).fetchall()
    
    cur.close()
    
    filtered_lb = [dict(libem[0]), dict(best[0]), dict(avg[0])]
    if uuid is not None:
        filtered_lb.extend([dict(u) for u in user])
    return sorted(filtered_lb, key=cmp_to_key(compare), reverse=True)

@app.post('/deleteuser/', tags=["Misc"])
async def delete_user(data: DeleteUser):
    ''' Delete a user from the database. Requires a password if the user is not a demo type. '''
    
    uuid = validate(data.uuid)
    session = get_session(uuid)
    
    if session['type'] not in secrets['demo_types']:
        if data.password is None:
            raise HTTPException(status_code=403, 
                                detail="Password required to delete this user.")
        elif data.password != secrets['password']:
            raise HTTPException(status_code=422, 
                                detail='Password is not correct. Your attempt has been logged.')
    
    cur = con.cursor()
    for table in ['sessions', 'matches', 'leaderboard']:
        cur.execute(f"DELETE FROM {table} WHERE uuid = ? AND type = ?",
                    (uuid, session['type']))
    con.commit()
    cur.close()

@app.post('/runsql/', include_in_schema=False)
async def run_sql(data: RunSql):
    ''' Run a SQL query. Requires a password. '''
    
    if data.password != secrets['password']:
        raise HTTPException(status_code=422, 
                            detail='Password is not correct. Your attempt has been logged.')
    
    cur = con.cursor()
    results = [dict(i) for i in cur.execute(data.query)]
    con.commit()
    cur.close()
    
    return results

# run the API
if __name__ == "__main__":
        uvicorn.run("serve:app", host="127.0.0.1", port=8000)
