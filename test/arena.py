import time
import requests

######################################
# May require changes
backend_url = 'http://localhost/api'
access_token = ""
######################################


def fetchURL(url, method='GET', json=None):
    if method == 'GET':
        return requests.get(f"{backend_url}{url}",
                            headers={
                                "Authorization": f"Bearer {access_token}"
                            })
    else:
        return requests.post(f"{backend_url}{url}",
                            headers={
                                "Authorization": f"Bearer {access_token}"
                            },
                            json=json)

if not access_token:
    access_token = input(f"Login at {backend_url}/login and get an access token: ")


# call info without logged in
response = requests.get(f'{backend_url}/info')
assert response.ok, f"Server error for /info: {response.content}"
response = response.json()
for item in ['auth', 'benchmarks']:
    assert item in response, "Wrong return for /info"
assert response['auth'] == False, "Wrongly authenticated for /info"

# call info with token
response = fetchURL('/info')
assert response.ok, f"Server error for /info: {response.content}"
response1 = response.json()
for item in ['auth', 'id', 'name', 'avatar', 'benchmarks']:
    assert item in response1, "Wrong return for /info"
assert response1['auth'], "Not authenticated for /info"

user_id = response1['id']
benchmark = list(response1['benchmarks'].keys())[0]
benchmark1 = list(response1['benchmarks'].keys())[1]
benchmark_size = response1['benchmarks'][benchmark]['size']

# info with token again, expect same return
response = fetchURL('/info')
assert response.ok, f"Server error for /info: {response.content}"
response2 = response.json()
assert 'id' in response2 and 'benchmarks' in response2, "Wrong return for /info"
assert response1['id'] == response2['id'], "Nondeterministic ID return"
assert response1['benchmarks'] == response2['benchmarks'], "Nondeterministic return"

# call /submit without /match, expect fail
response = fetchURL('/submit', method='POST',
                    json={'answers': [1 for _ in range(benchmark_size)], 
                          'display_name': 'Test'})
assert response.status_code == 403, "Call /submit without /match"

# call /match, expect normal return
response = fetchURL(f'/match?&benchmark={benchmark}')
assert response.ok, f"Server error for /match: {response.content}"
dataset = response.json()['pairs']
assert len(dataset) == benchmark_size

# call /match again, expect reject due to multiple calls
response = fetchURL(f'/match?&benchmark={benchmark}')
assert response.status_code == 403, "Multiple calls allowed for /match"

time.sleep(3)

# call /submit, expect normal return
response = fetchURL('/submit', method='POST',
                    json={'answers': [1 for _ in range(benchmark_size)], 
                          'display_name': 'Test'})
assert response.ok, f"Server error for /submit: {response.content}"
submit = response.json()
assert 'score' in submit, "Wrong return for /submit"
assert 'time' in submit and 3 <= submit['time'] <= 5, f"Wrong time: {submit['time']}"

avg_time = round(submit['time'] / benchmark_size, 3)

# call /leaderboard
response = fetchURL(f'/leaderboard?benchmark={benchmark}')
assert response.ok, f"Server error for /leaderboard: {response.content}"
leaderboard = response.json()
seen = 0
for l in leaderboard:
    if l['id'] == user_id:
        seen += 1
        if seen == 1:
            assert l['pairs'] == benchmark_size, f"Wrong leaderboard pairs: {l['pairs']}"
            assert l['name'] == 'Test', "Wrong leaderboard name"
            assert avg_time == round(l['avg_time'], 3), "Wrong leaderboard time"
assert seen >= 1, "ID not in leaderboard"
assert seen == 1, "Multiple entries in leaderboard"

# call /submit again, expect fail
response = fetchURL(f'/submit', method='POST',
                    json={'answers': [1 for _ in range(benchmark_size)], 
                          'display_name': 'Test'})
assert response.status_code == 403, "Call /submit twice"

# call /match, expect normal return
response = fetchURL(f'/match?benchmark={benchmark}')
assert response.ok, f"Server error for /match: {response.content}"
dataset = response.json()['pairs']
assert len(dataset) == benchmark_size, "Wrong returned length for /match"

# call /submit with wrong number of answers, expect fail
response = fetchURL('/submit', method='POST',
                    json={'answers': [1 for _ in range(benchmark_size-1)], 
                          'display_name': 'Test'})
assert response.status_code == 400, "Call /submit with wrong answers length"

benchmark = benchmark1

# call /matchone, expect normal return
response = fetchURL(f'/matchone?benchmark={benchmark}')
assert response.ok, f"Server error for /matchone: {response.content}"
pair1 = response.json()

# call /matchone, expect same return as before
response = fetchURL(f'/matchone?benchmark={benchmark}')
assert response.ok, f"Server error for /matchone: {response.content}"
pair2 = response.json()
assert pair1 == pair2, "Multiple calls to /match lead to differnt returns"

time.sleep(1)

# call /submitone
response = fetchURL(f'/submitone', method='POST',
                    json={'benchmark': benchmark, 
                          'answer': False, 'time': 1.01})
assert response.ok, f"Server error for /submitone: {response.content}"
submit = response.json()
assert 'label' in submit, "Wrong return for /submitone"

# call /leaderboard
response = fetchURL(f'/leaderboard?benchmark={benchmark}')
assert response.ok, f"Server error for /leaderboard: {response.content}"
leaderboard = response.json()
seen = 0
for l in leaderboard:
    if l['id'] == user_id:
        seen += 1
        if seen == 1:
            assert l['pairs'] == 1, f"Wrong leaderboard pairs: {l['pairs']}"
            # assert round(l['avg_time'], 2) == 1.01, f"Wrong leaderboard time: {l['avg_time']}"
assert seen >= 1, "ID not in leaderboard"
assert seen == 1, "Extra entries in leaderboard"

# call /submitone again, expect fail
response = fetchURL(f'/submitone', method='POST',
                    json={'benchmark': benchmark, 
                          'answer': False, 'time': 1.01})
assert response.status_code == 403, f"Submit twice for /submitone {response.content}"

# call /matchone, expect a new pair
response = fetchURL(f'/matchone?benchmark={benchmark}')
assert response.ok, f"Server error for /matchone: {response.content}"
pair3 = response.json()
assert pair1 != pair3, "All calls to /match lead to same pair being returned"

time.sleep(1)

# call /submitone
response = fetchURL(f'/submitone', method='POST',
                    json={'benchmark': benchmark, 
                          'answer': False, 'time': 12.34})
assert response.ok, f"Server error for /submitone: {response.content}"
submit = response.json()
assert 'label' in submit, "Wrong return for /submitone"

# call /leaderboard
response = fetchURL(f'/leaderboard?benchmark={benchmark}')
assert response.ok, f"Server error for /leaderboard: {response.content}"
leaderboard = response.json()
seen = 0
for l in leaderboard:
    if l['id'] == user_id:
        seen += 1
        if seen == 1:
            assert l['pairs'] == 2, f"Wrong leaderboard pairs: {l['pairs']}"
            assert l['avg_time'] <= 3, "Wrong leaderboard time"
assert seen >= 1, "ID not in leaderboard"
assert seen == 1, "Multiple entries in leaderboard"

# delete user
response = fetchURL('/deleteuser', method='POST')
assert response.ok, f"Server error for /deleteuser: {response.content}"

print("All tests passed.")
