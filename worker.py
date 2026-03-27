import socket
import json
import argparse
from utils import jaccard_similarity

HOST = '127.0.0.1'
PORT = 5000

def run_worker():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Could not connect to master at {HOST}:{PORT}")
        return

    # register as worker
    sock.sendall((json.dumps({'role': 'worker'}) + '\n').encode('utf-8'))
    print(f"Connected to master at {HOST}:{PORT}")
    
    f = sock.makefile('r', encoding='utf-8')
    try:
        while True:
            line = f.readline()
            if not line:
                break
            
            task = json.loads(line)
            job_id = task['job_id']
            target_name = task['target_name']
            threshold = task['threshold']
            data_chunk = task['data']
            
            # process
            results = []
            for name in data_chunk:
                sim = jaccard_similarity(target_name, name)
                if sim >= threshold:
                    results.append((name, sim))
                    
            # send response
            response = {
                'job_id': job_id,
                'results': results
            }
            sock.sendall((json.dumps(response) + '\n').encode('utf-8'))
    except Exception as e:
        print(f"Worker disconnected: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    run_worker()
