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

First login at https://arena.libem.org
and copy the access token in the profile dropdown

```
import requests
import libem

access_token = '' # Paste access token here

# Call /info to get the available benchmarks
response = requests.get('https://arena.libem.org/api/info').json()
benchmarks = response['benchmarks']

# Get the first benchmark name
benchmark = list(response1['benchmarks'].keys())[0]

# Then call /match with the benchmark name
response = requests.get(
                f'https://arena.libem.org/api/match?benchmark={benchmark}',
                headers={
                    'Authorization': f'Bearer {access_token}'
                }).json()
pairs = response['pairs']

# Separate the pairs into 'left' and 'right',
# then use Libem to get the answers
left, right = [], []
for pair in pairs:
    left.append(pair['left'])
    right.append(pair['right'])
answers = libem.match(left, right)

# Call /submit with the list of answers to get the score and time
response = requests.post(
                f'arena.libem.org/api/submit', 
                headers={
                    'Authorization': f'Bearer {access_token}'
                },
                json={'answers': answers, 
                      'display_name': 'Demo'}).json()
score, time = response['score'], response['time']
```

## Local setup

#### Kubernetes

To host Arena through kubernetes:

```
libem/arena> make up
```

The frontend will be hosted at http://localhost and the API will be at http://localhost/api.

To stop hosting:

```
libem/arena> make down
```

To remove PVC storage:

```
libem/arena> make delete
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