import os
import json
import sqlite3
import uvicorn
from fastapi import FastAPI
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
    dataset: str
    index: int
    answer: bool
class Leaderboard(BaseModel):
    uuid: str
    name: str
    dataset: str
    pairs: int
    score: int | float
    avg_time: int | float

def read_demo(ds_name):
    ds_name = ds_name.lower()
    path = os.path.join(ds.LIBEM_SAMPLE_DATA_PATH, ds_name)
    demo_file = os.path.join(os.path.join(path, 'demo'), 'demo.ndjson')
    with open(demo_file, 'r') as f:
        dataset = []
        for line in f:
            dataset.append(json.loads(line))
        return dataset

def read_result(ds_name):
    ds_name = ds_name.lower()
    results_folder = os.path.join(os.path.join(ds.LIBEM_SAMPLE_DATA_PATH, 'libem-results'), 'demo')
    file = os.path.join(results_folder, f'{ds_name}.json')
    with open(file, 'r') as f:
        return json.load(f)

# datasets
dataset_list = {
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
datasets = {
    name: {
        'description': d.description,
        'dataset': read_demo(name)
    }
    for name, d in dataset_list.items()
}
metadata = {
    name: {
            'description': v['description'],
            'size': len(v['dataset'])
    }
    for name, v in datasets.items()
}
libem_results = {
    name: read_result(name) for name in dataset_list.keys()
}

# sql db (results and leaderboard)
con = sqlite3.connect("results.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS matches("
            "uuid varchar(40) not null, "
            "entity_1 varchar(5000), "
            "entity_2 varchar(5000), "
            "pred int not null, "
            "label int not null)")
cur.execute("CREATE TABLE IF NOT EXISTS leaderboard("
            "uuid varchar(40) not null, "
            "name varchar(100), "
            "dataset varchar(50) not null, "
            "pairs int not null, "
            "score float not null, "
            "avg_time float not null)")

res = cur.execute("SELECT * FROM leaderboard WHERE name='Libem'")
if res.fetchone() is None:
    # add libem results to leaderboard
    cur.executemany("INSERT INTO leaderboard VALUES(?, ?, ?, ?, ?, ?)", [(
                        "0", "Libem", name, metadata[name]['size'], 
                        libem_results[name]['stats']['f1'], 
                        round(libem_results[name]['stats']['latency'] / metadata[name]['size'], 3))
                    for name in dataset_list.keys()])
    con.commit()
cur.close()

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
async def init():
    ''' Return the neccessary metadata. '''
    return metadata

@app.get('/fetch/')
async def fetch(dataset: str, index: int):
    ''' Fetch a single pair from a dataset. '''
    return {
        'left': datasets[dataset]['dataset'][index]['left'],
        'right': datasets[dataset]['dataset'][index]['right'],
        'libem_time': libem_results[dataset]['results'][index]['latency']
    }

@app.post('/submit/')
async def submit(data: Submit):
    ''' Save the answer and return the label. '''
    pair = datasets[data.dataset]['dataset'][data.index]
    libem_res = libem_results[data.dataset]['results'][data.index]
    
    cur = con.cursor()
    cur.execute("INSERT INTO matches VALUES(?, ?, ?, ?, ?)", (
        data.uuid, json.dumps(pair['left']), json.dumps(pair['right']), 
        data.answer, pair['label']))
    con.commit()
    cur.close()
    
    return {
        'label': pair['label'],
        'libem_pred': libem_res['pred'] == 'yes'
    }

@app.get('/leaderboard/')
async def get_leaderboard(dataset: str, uuid: str):
    cur = con.cursor()
    libem = cur.execute("SELECT * FROM leaderboard WHERE dataset = ? AND uuid = ? LIMIT 1", 
                        (dataset, "0")).fetchall()
    best = cur.execute(f"SELECT '1' as uuid, 'Users Best' as name, '{dataset}' as dataset, "
                       "COALESCE(MAX(pairs), 0) as pairs, COALESCE(MAX(score), 0) as score, "
                       "COALESCE(MAX(avg_time), 0) as avg_time "
                       "FROM leaderboard WHERE dataset = ? AND uuid != ? ORDER BY score DESC LIMIT 1", 
                       (dataset, "0")).fetchall()
    avg = cur.execute(f"SELECT '2' as uuid, 'Users Avg' as name, '{dataset}' as dataset, "
                      "COALESCE(AVG(pairs), 0) as pairs, COALESCE(AVG(score), 0) as score, "
                      "COALESCE(AVG(avg_time), 0) as avg_time "
                      "FROM leaderboard WHERE dataset = ? AND uuid != ?",
                      (dataset, "0")).fetchall()
    user = cur.execute("SELECT * FROM leaderboard WHERE dataset = ? AND uuid = ?",
                       (dataset, uuid)).fetchall()
    cur.close()
    
    filtered_lb = [dict(libem[0]), dict(best[0]), dict(avg[0])] + [dict(u) for u in user]
    return sorted(filtered_lb, key=cmp_to_key(compare), reverse=True)

@app.post('/leaderboard/')
async def post_leaderboard(data: Leaderboard):
    cur = con.cursor()
    cur.execute("INSERT INTO leaderboard VALUES(?, ?, ?, ?, ?, ?)", 
                (data.uuid, data.name, data.dataset, 
                 data.pairs, data.score, data.avg_time))
    con.commit()
    cur.close()

# run the API
if __name__ == "__main__":
        uvicorn.run("serve:app", host="127.0.0.1", port=8000)
