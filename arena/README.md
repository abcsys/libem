# Libem Arena

Libem Arena is a simple web "game" which allows crowd-sourcing entity matching over a web page.

Two entities are given, and the user has to decide if they are the same or not by clicking yes or no button.
- Pairs of entities are sampled from the datasets on different categories
- User selections are logged anonymously using a session UUID
- User performance is compared to Libem and aggregate stats of all other users

## Frontend

Libem Arena is available to try out at https://arena.libem.org. See the [screenshots](#screenshots) section for more details.

## API - [Docs](https://arena.libem.org/api/docs)

A benchmarking tool for EM.
Libem Arena supports benchmarking both users (preferably through the frontend) and EM models (through the API).

The API is available to try out at https://arena.libem.org/api/.

### Usage

To benchmark Libem using Libem Arena:

```
import requests
import libem

# First call /init to get a session UUID, 
# make sure to pass in token=model
response = requests.get('arena.libem.org/api/init?token=model').json()
uuid, benchmarks = response['uuid'], response['benchmarks']

# Then call /match with the UUID to get the pairs from the first benchmark
response = requests.get(f'arena.libem.org/api/match?
                          uuid={uuid}&
                          benchmark={benchmarks[0]}').json()
pairs = response['pairs']

# Separate the pairs into 'left' and 'right' 
# then call Libem to get the answers
left, right = [], []
for pair in pairs:
    left.append(pair['left'])
    right.append(pair['right'])
answers = libem.match(left, right)

# Call /submit with the list of answers to get the score and time
response = requests.post(f'arena.libem.org/api/submit', 
                         json={'uuid': uuid, 
                               'answers': answers, 
                               'display_name': 'Test'}).json()
score, time = response['score'], response['time']
```

## Local setup

#### Docker

To host both the frontend and backend through docker:

```
libem/arena> make docker-up
```

The frontend will be hosted at http://localhost:5000/ and the backend will be at http://localhost:8000/.

To stop hosting:

```
libem/arena> make docker-down
```

## Screenshots

### Home
![Libem Arena Homescreen](./docs/arena_home.png)

### Match
![Libem Arena Homescreen](./docs/arena_select.png)

## Results
![Libem Arena Homescreen](./docs/arena_result.png)

## Leaderboard
![Libem Arena Homescreen](./docs/arena_leaderboard.png)