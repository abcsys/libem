import time
import requests

backend_url = 'http://127.0.0.1:8000'

# init as user
response = requests.get(f'{backend_url}/init/?token=demo_user&uuid=123')
assert response.ok, f"Server error for /init: {response.content}"
response1 = response.json()
assert 'uuid' in response1 and 'benchmarks' in response1, "Wrong return for /init"

uuid, benchmark = response1["uuid"], list(response1['benchmarks'].keys())[0]
benchmark_size = response1['benchmarks'][benchmark]['size']

# init as user again, expect same return
response = requests.get(f'{backend_url}/init/?token=demo_user')
assert response.ok, f"Server error for /init: {response.content}"
response2 = response.json()
assert 'uuid' in response2 and 'benchmarks' in response2, "Wrong return for /init"
assert response1['uuid'] == response2['uuid'], "Nondeterministic UUID return"
assert response1['benchmarks'] == response2['benchmarks'], "Nondeterministic return"

# call /match, expect reject due to wrong user type
response = requests.get(f'{backend_url}/match/?uuid={uuid}&benchmark={benchmark}')
assert response.status_code == 403, "No user type check for /match"

# init as model
response = requests.get(f'{backend_url}/init/?token=demo_model')
assert response.ok, f"Server error for /init: {response.content}"
response3 = response.json()
assert 'uuid' in response3 and 'benchmarks' in response3, "Wrong return for /init"
assert response1['uuid'] == response3['uuid'], "Nondeterministic UUID return"
assert response1['benchmarks'] == response3['benchmarks'], "Nondeterministic return"

# call /submit without /match, expect fail
response = requests.post(f'{backend_url}/submit/', 
                         json={'uuid': uuid, 
                               'answers': [1 for _ in range(benchmark_size)], 
                               'display_name': 'Test'})
assert response.status_code == 403, "Call /submit without /match"

# call /match, expect normal return
response = requests.get(f'{backend_url}/match/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /match: {response.content}"
dataset = response.json()['pairs']
assert len(dataset) == benchmark_size

# call /match again, expect reject due to multiple calls
response = requests.get(f'{backend_url}/match/?uuid={uuid}&benchmark={benchmark}')
assert response.status_code == 403, "Multiple calls allowed for /match"

time.sleep(3)

# call /submit, expect normal return
response = requests.post(f'{backend_url}/submit/', 
                         json={'uuid': uuid, 
                               'answers': [1 for _ in range(benchmark_size)], 
                               'display_name': 'Test'})
assert response.ok, f"Server error for /submit: {response.content}"
submit = response.json()
assert 'score' in submit, "Wrong return for /submit"
assert 'time' in submit and 3 <= submit['time'] <= 4, "Wrong time"

avg_time = round(submit['time'] / benchmark_size, 3)

# call /leaderboard
response = requests.get(f'{backend_url}/leaderboard/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /leaderboard: {response.content}"
leaderboard = response.json()
seen = 0
for l in leaderboard:
    if l['uuid'] == uuid:
        seen += 1
        if seen == 1:
            assert l['pairs'] == benchmark_size, "Wrong leaderboard pairs"
            assert l['name'] == 'Test', "Wrong leaderboard name"
            assert avg_time == round(l['avg_time'], 3), "Wrong leaderboard time"
assert seen >= 1, "UUID not in leaderboard"
assert seen == 1, "Multiple entries in leaderboard"

# call /submit again, expect fail
response = requests.post(f'{backend_url}/submit/', 
                         json={'uuid': uuid, 
                               'answers': [1 for _ in range(benchmark_size)], 
                               'display_name': 'Test'})
assert response.status_code == 403, "Call /submit twice"

# call /match, expect normal return
response = requests.get(f'{backend_url}/match/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /match: {response.content}"
dataset = response.json()['pairs']
assert len(dataset) == benchmark_size, "Wrong returned length for /match"

# call /submit with wrong number of answers, expect fail
response = requests.post(f'{backend_url}/submit/', 
                         json={'uuid': uuid, 
                               'answers': [1 for _ in range(benchmark_size-1)], 
                               'display_name': 'Test'})
assert response.status_code == 400, "Call /submit with wrong answers length"

# init as user again
response = requests.get(f'{backend_url}/init/?token=demo_user')
assert response.ok, f"Server error for /init: {response.content}"
response4 = response.json()
assert response4['uuid'] == uuid, "Nondeterministic UUID return"

# call /matchone, expect normal return
response = requests.get(f'{backend_url}/matchone/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /matchone: {response.content}"
pair1 = response.json()

# init as user again, expect no changes
response = requests.get(f'{backend_url}/init/?token=demo_user')
assert response.ok, f"Server error for /init: {response.content}"
response4 = response.json()
assert response4['uuid'] == uuid, "Nondeterministic UUID return"

# call /matchone, expect same return as before
response = requests.get(f'{backend_url}/matchone/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /matchone: {response.content}"
pair2 = response.json()
assert pair1 == pair2, "Multiple calls to /match lead to differnt returns"

time.sleep(1)

# call /submitone
response = requests.post(f'{backend_url}/submitone/', 
                         json={'uuid': uuid, 
                               'benchmark': benchmark, 
                               'answer': False, 'time': 1.01})
assert response.ok, f"Server error for /submitone: {response.content}"
submit = response.json()
assert 'label' in submit, "Wrong return for /submitone"

# call /leaderboard
response = requests.get(f'{backend_url}/leaderboard/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /leaderboard: {response.content}"
leaderboard = response.json()
seen = 0
for l in leaderboard:
    if l['uuid'] == uuid:
        seen += 1
        if seen == 1:
            # assert l['pairs'] == 1, "Wrong leaderboard pairs"
            assert round(l['avg_time'], 2) == 1.01, "Wrong leaderboard time"
assert seen >= 1, "UUID not in leaderboard"
assert seen == 1, "Multiple entries in leaderboard"

# call /submitone again, expect fail
response = requests.post(f'{backend_url}/submitone/', 
                         json={'uuid': uuid, 
                               'benchmark': benchmark, 
                               'answer': False, 'time': 1.01})
assert response.status_code == 403, "Submit twice for /submitone"

# call /matchone, expect a new pair
response = requests.get(f'{backend_url}/matchone/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /matchone: {response.content}"
pair3 = response.json()
assert pair1 != pair3, "All calls to /match lead to same pair being returned"

time.sleep(1)

# call /submitone
response = requests.post(f'{backend_url}/submitone/', 
                         json={'uuid': uuid, 
                               'benchmark': benchmark, 
                               'answer': False, 'time': 12.34})
assert response.ok, f"Server error for /submitone: {response.content}"
submit = response.json()
assert 'label' in submit, "Wrong return for /submitone"

# call /leaderboard
response = requests.get(f'{backend_url}/leaderboard/?uuid={uuid}&benchmark={benchmark}')
assert response.ok, f"Server error for /leaderboard: {response.content}"
leaderboard = response.json()
seen = 0
for l in leaderboard:
    if l['uuid'] == uuid:
        seen += 1
        if seen == 1:
            assert l['pairs'] == 2, "Wrong leaderboard pairs"
            assert l['avg_time'] <= 2, "Wrong leaderboard time"
assert seen >= 1, "UUID not in leaderboard"
assert seen == 1, "Multiple entries in leaderboard"

# delete user as type demo_user
response = requests.post(f'{backend_url}/deleteuser/', 
                         json={'uuid': uuid})
assert response.ok, f"Server error for /deleteuser: {response.content}"

# init as model
response = requests.get(f'{backend_url}/init/?token=demo_model')
assert response.ok, f"Server error for /init: {response.content}"

# delete user as type demo_model
response = requests.post(f'{backend_url}/deleteuser/', 
                         json={'uuid': uuid})
assert response.ok, f"Server error for /deleteuser: {response.content}"
