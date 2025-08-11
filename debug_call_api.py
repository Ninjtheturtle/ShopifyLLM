import requests, time, json

base = 'http://127.0.0.1:5000'

print('GET /api/config')
print(requests.get(base + '/api/config').json())

payload = {"prompt": "add some workout clothes for men and women to the store"}
print('POST /api/create-store', payload)
resp = requests.post(base + '/api/create-store', json=payload)
print('Create response:', resp.status_code, resp.text)

if resp.ok:
    job = resp.json().get('job_id')
    for i in range(20):
        time.sleep(1.0)
        r = requests.get(f"{base}/api/job-status/{job}")
        try:
            data = r.json()
        except Exception:
            print('Non-JSON:', r.text)
            break
        print('Status:', data.get('status'), data.get('progress'))
        if data.get('status') in ('completed','failed'):
            print(json.dumps(data, indent=2))
            break
