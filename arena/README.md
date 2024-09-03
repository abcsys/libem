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

## Local setup

#### Docker

To host both the frontend and backend through docker:

```
libem/arena> docker-compose up --build
```

#### Backend

The backend is self-contanined in `./serve.py`, and can be hosted using uvicorn by running

```
libem/arena> python serve.py
```

#### Frontend

The frontend can be compiled into static HTML in `./dist` by running

```
libem/arena> npm i # installs all dependencies
libem/arena> npm run build
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