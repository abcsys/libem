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

# POST structs
class Submit(BaseModel):
    uuid: str
    answers: list
    display_name: str
class SubmitOne(BaseModel):
    uuid: str
    benchmark: str
    answer: bool
    time: int | float = -1
class RunSql(BaseModel):
    query: str
    password: str

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

# benchmarks
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

# sql dbs 
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

# read in secrets
home_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(os.path.join(home_dir, 'secrets'), 'secrets.json'), 'r') as f:
    secrets = json.load(f)

def compare(a, b):
    return a['score'] - b['score']

app = FastAPI()

# handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get('/init/')
async def init(request: Request, token: str = '', uuid: str = ''):
    ''' Return benchmark info and generates an UUID if not given. '''

    # check if provided uuid and token are valid
    try:
        uuid = str(uuidlib.UUID(uuid))
    except ValueError:
        # if not, generate a new uuid from the incoming IP address
        ip_hex = hashlib.md5(request.client.host.encode("UTF-8")).hexdigest()
        uuid = str(uuidlib.UUID(hex=ip_hex))
    if token not in secrets['tokens'].keys():
        raise HTTPException(status_code=422, detail='Bad token.')

    # add to sessions db if not exists, or update token
    cur = con.cursor()
    session = cur.execute("SELECT type FROM sessions WHERE uuid = ?",
              (uuid,)).fetchall()
    if len(session) == 0:
        cur.execute("INSERT INTO sessions(uuid, type, seed) VALUES(?, ?, ?)", 
                    (uuid, secrets['tokens'][token], random.randint(0, 0xffffffff)))
    else:
        cur.execute("UPDATE sessions SET type = ?, seed = ?, matching = ? "
                    "WHERE uuid = ?", 
                    (secrets['tokens'][token], random.randint(0, 0xffffffff), 0, uuid))
    con.commit()
    cur.close()
    
    return {
        'uuid': uuid,
        'benchmarks': metadata
    }

@app.get('/match/')
async def match(uuid: str, benchmark: str):
    ''' Return all pairs from a benchmark. '''
    
    # check validity of uuid and benchmark
    try:
        uuid = str(uuidlib.UUID(uuid))
    except ValueError:
        raise HTTPException(status_code=422, 
                            detail='UUID is not valid. '
                                   'Call /init to get a valid UUID first.')
    if benchmark not in benchmark_list.keys():
        raise HTTPException(status_code=422, detail='Benchmark not found.')
    
    cur = con.cursor()
    
    # get user type, seed, and matching from session
    session = cur.execute("SELECT type, seed, matching FROM sessions WHERE uuid = ?",
              (uuid,)).fetchall()
    if len(session) == 0:
        raise HTTPException(status_code=400, 
                            detail='UUID does not exist.'
                                   'Call /init with your UUID first.')
    session = dict(session[0])
    
    if session['type'] in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /match_one instead "
                                   "or call /init again with a different token.")
    # only allow one active matching request at once
    if session['matching'] == 1:
        raise HTTPException(status_code=403, 
                            detail="Sumbit the previous matching request first "
                                   "or call /init again to reset.")
    
    cur.close()
    
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
        'pairs': pairs
    }

@app.post('/submit/')
async def submit(data: Submit):
    ''' Save all answers and return stats. '''
    
    submit_time = time.time()
    
    # check validity of uuid
    try:
        uuid = str(uuidlib.UUID(data.uuid))
    except ValueError:
        raise HTTPException(status_code=422, 
                            detail='UUID is not valid. '
                                   'Call /init to get a valid UUID first.')
    
    cur = con.cursor()
    
    # get user info from session
    session = cur.execute("SELECT * FROM sessions WHERE uuid = ?",
              (uuid,)).fetchall()
    if len(session) == 0:
        raise HTTPException(status_code=400, 
                            detail='UUID does not exist.'
                                   'Call /init with your UUID first.')
    session = dict(session[0])
    benchmark = session['benchmark']
    
    if session['type'] in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /submit_one instead "
                                   "or call /init again with a different token.")
    
    if session['matching'] == 0:
        raise HTTPException(status_code=403, 
                            detail="Request a new benchmark with /match first.")
    
    # set matching to false
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
    print(tp, tn, fp, fn)
    avg_time = (submit_time - session['timestamp']) / len(data.answers)
    
    cur = con.cursor()
    
    # get current leaderboard entry
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND uuid = ? AND name = ?",
                      (benchmark, uuid, data.display_name)).fetchall()
    
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
        "score": f1,
        "avg_time": avg_time
    }

@app.get('/match_one/')
async def match_one(uuid: str, benchmark: str):
    ''' Return the next pair from a benchmark. '''
    
    # check validity of uuid and benchmark
    try:
        uuid = str(uuidlib.UUID(uuid))
    except ValueError:
        raise HTTPException(status_code=422, 
                            detail='UUID is not valid. '
                                   'Call /init to get a valid UUID first.')
    if benchmark not in benchmark_list.keys():
        raise HTTPException(status_code=422, detail='Benchmark not found.')
    
    cur = con.cursor()
    
    # get user type and seed from session
    session = cur.execute("SELECT type, seed FROM sessions WHERE uuid = ?",
              (uuid,)).fetchall()
    if len(session) == 0:
        raise HTTPException(status_code=400, 
                            detail='UUID does not exist.'
                                   'Call /init with your UUID first.')
    session = dict(session[0])
    
    if session['type'] not in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /match instead "
                                   "or call /init again with a different token.")
    
    # get current number of pairs matched from leaderboard
    lb_entry = cur.execute("SELECT pairs FROM leaderboard "
                      "WHERE benchmark = ? AND uuid = ?",
                      (benchmark, uuid)).fetchall()
    # get the last matched pair
    if len(lb_entry) == 0:
        lb_entry = {}
    else:
        lb_entry = dict(lb_entry[0])
    pairs = lb_entry.get('pairs', 0)
        
    cur.close()
    
    # if no more pairs, return error
    if pairs >= metadata[benchmark]['size']:
        raise HTTPException(status_code=204, detail='End of benchmark.')
    
    # sample the next pair
    random.seed(session['seed'])
    index = random.sample(range(0, metadata[benchmark]['size']), pairs + 1)[-1]
    pair = benchmarks[benchmark]['benchmark'][index]
    
    return {
        'index': pairs,
        'left': pair['left'],
        'right': pair['right']
    }

@app.post('/submit_one/')
async def submit_one(data: SubmitOne):
    ''' Save the answer and return the label. '''
    
    # check validity of uuid and benchmark
    try:
        uuid = str(uuidlib.UUID(data.uuid))
    except ValueError:
        raise HTTPException(status_code=422, 
                            detail='UUID is not valid. '
                                   'Call /init to get a valid UUID first.')
    if data.benchmark not in benchmark_list.keys():
        raise HTTPException(status_code=422, detail='Benchmark not found.')
    
    cur = con.cursor()
    
    # get user type and seed from session
    session = cur.execute("SELECT type, seed FROM sessions WHERE uuid = ?",
              (uuid,)).fetchall()
    if len(session) == 0:
        raise HTTPException(status_code=400, 
                            detail='UUID does not exist.'
                                   'Call /init with your UUID first.')
    session = dict(session[0])
    
    if session['type'] not in secrets['user_types']:
        raise HTTPException(status_code=403, 
                            detail="User type not allowed. Use /submit instead "
                                   "or call /init again with a different token.")
    
    # get current leaderboard entry
    lb_entry = cur.execute("SELECT * FROM leaderboard "
                      "WHERE benchmark = ? AND uuid = ?",
                      (data.benchmark, uuid)).fetchall()
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
    
    # add submission to matches db
    cur = con.cursor()
    cur.execute("INSERT INTO matches VALUES(?, ?, ?, ?, ?)", (
        data.uuid, json.dumps(pair['left']), json.dumps(pair['right']), 
        data.answer, pair['label']))
    
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
    
    # if leaderboard entry does not exist, create entry, otherwise update entry
    if len(lb_entry) == 0:
        cur.execute("INSERT INTO leaderboard(uuid, type, benchmark, pairs, tp, fp, tn, fn, score, avg_time) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (uuid, 'user', data.benchmark, 1, tp, fp, tn, fn, f1, data.time))
    else:
        avg_time = (lb_entry['avg_time'] * pairs + data.time) / (pairs + 1)
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

@app.get('/leaderboard/')
async def get_leaderboard(benchmark: str, uuid: str):
    ''' Get the leaderboard for a benchmark. '''
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
    user = cur.execute("SELECT * FROM leaderboard WHERE benchmark = ? AND uuid = ?",
                       (benchmark, uuid)).fetchall()
    cur.close()
    
    filtered_lb = [dict(libem[0]), dict(best[0]), dict(avg[0])] + [dict(u) for u in user]
    return sorted(filtered_lb, key=cmp_to_key(compare), reverse=True)

@app.post('/run_sql/')
async def rul_sql(data: RunSql):
    if data.password != secrets['sql_password']:
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
