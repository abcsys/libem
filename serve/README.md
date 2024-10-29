# Libem Serve

Libem Serve is a REST API to serve Libem.

## API - [Docs](https://serve.libem.org/docs)

The API is available to try out at https://serve.libem.org/.

### Usage

First get an access token from https://serve.libem.org/.

Then call any API endpoint:

```
import requests

out = requests.post(
        'https://serve.libem.org/match',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'left': 'apple', 
            'right': 'orange'
        }).json()

print(out['response'])
```

## Local setup

```
libem> make serve
```

The app will be hosted at http://localhost:8080/.
