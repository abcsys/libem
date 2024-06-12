import os
import json
import aiofile
import uvicorn
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json

import libem.prepare.datasets as ds
from libem.prepare.datasets import (abt_buy, amazon_google, beer, dblp_acm, 
                                    dblp_scholar, fodors_zagats, itunes_amazon, 
                                    walmart_amazon, challenging)

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

# POST struct
class Submit(BaseModel):
    uuid: str
    dataset: str
    index: int
    answer: bool

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

# run the API
if __name__ == "__main__":
        uvicorn.run("serve:app", host="127.0.0.1", port=8000)
