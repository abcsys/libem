import os
import json
import aiofile
import uvicorn
from datetime import datetime
from pathlib import Path
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

# results log file
results_folder = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'results')
Path(results_folder).mkdir(parents=True, exist_ok=True)

# leaderboard and sort function
lb_file = os.path.join(results_folder, 'leaderboard.json')
leaderboard = None
try:
    with open(lb_file, 'r') as f:
        leaderboard = json.load(f)
except:
    pass

if leaderboard == None:
    # add libem results to leaderboard
    leaderboard = {
        name: [{
                "uuid": "0",
                "name": "Libem", 
                "dataset": name, 
                "pairs": metadata[name]['size'],
                "score": libem_results[name]['stats']['f1'], 
                "avg_time": round(libem_results[name]['stats']['latency'] / metadata[name]['size'], 3)},
               {
                "uuid": "1",
                "name": "Users Best", 
                "dataset": name, 
                "pairs": 0,
                "score": 0, 
                "avg_time": 0},
               {
                "uuid": "2",
                "name": "Users Average", 
                "dataset": name, 
                "pairs": 0,
                "score": 0, 
                "avg_time": 0},
               ]
        for name in dataset_list.keys()
    }
    # save to file
    with open(lb_file, 'w') as out:
        json.dump(leaderboard, out)

def compare(a, b):
    return a['score'] - b['score']

app = FastAPI()

# handle CORS
app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://localhost", "http://localhost:3000", "http://localhost:5000"],
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
    log_file = os.path.join(results_folder, f'{datetime.now().strftime("%Y-%m-%d")}.ndjson')
    pair = datasets[data.dataset]['dataset'][data.index]
    libem_res = libem_results[data.dataset]['results'][data.index]
    
    async with aiofile.async_open(log_file, 'a') as out:
        await out.write(json.dumps({
            'uuid': data.uuid,
            'entity_1': pair['left'],
            'entity_2': pair['right'],
            'pred': data.answer,
            'label': pair['label']
        }) + '\n')
        await out.flush()
    
    return {
        'label': pair['label'],
        'libem_pred': libem_res['pred'] == 'yes'
    }

@app.get('/leaderboard/')
async def get_leaderboard(dataset: str, uuid: str):
    try:
        with open(lb_file, 'r') as f:
            leaderboard = json.load(f)
    except:
        pass
    
    filtered_lb = [e for e in leaderboard[dataset] if e['uuid'] in ['0', '1', '2', uuid]]
    return sorted(filtered_lb, key=cmp_to_key(compare), reverse=True)

@app.post('/leaderboard/')
async def post_leaderboard(data: Leaderboard):
    try:
        with open(lb_file, 'r') as f:
            leaderboard = json.load(f)
    except:
        pass
    
    for i, entry in enumerate(leaderboard[data.dataset]):
        if entry['name'] == 'Users Best' and data.score > entry['score']:
            leaderboard[data.dataset][i] = {
                "uuid": '1',
                "name": "Users Best", 
                "dataset": data.dataset, 
                "pairs": data.pairs,
                "score": data.score, 
                "avg_time": data.avg_time
            }
        elif entry['name'] == 'Users Average':
            leaderboard[data.dataset][i] = {
                "uuid": '2',
                "name": "Users Average", 
                "dataset": data.dataset, 
                "pairs": entry['pairs'] + data.pairs,
                "score": (entry['score'] * entry['pairs'] + data.score * data.pairs) / (entry['pairs'] + data.pairs), 
                "avg_time": (entry['avg_time'] * entry['pairs'] + data.avg_time * data.pairs) / (entry['pairs'] + data.pairs)
            }
    
    leaderboard[data.dataset].append(json.loads(data.model_dump_json()))
    
    # save to file
    async with aiofile.async_open(lb_file, 'w') as out:
        await out.write(json.dumps(leaderboard))
        await out.flush()

# run the API
if __name__ == "__main__":
        uvicorn.run("serve:app", host="127.0.0.1", port=8000)
