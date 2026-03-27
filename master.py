import socket
import threading
import json
import uuid
import time
from queue import Queue, Empty

HOST = '127.0.0.1'
PORT = 5000

class MasterNode:
    def __init__(self, data_file):
        print(f"Loading data from {data_file}...")
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                self.data = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(self.data)} records.")
        except FileNotFoundError:
            print(f"File {data_file} not found. Run generate_data.py first.")
            self.data = []

        self.workers = {}  # socket -> dict with lock
        self.workers_lock = threading.Lock()
        
        self.job_results = {} # job_id -> list of results
        self.job_locks = {} # job_id -> event to wait on
        self.job_expected = {} # job_id -> int
        
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(100)
        print(f"Master listening on {HOST}:{PORT}")
        
        try:
            while True:
                client_sock, addr = server.accept()
                threading.Thread(target=self.handle_connection, args=(client_sock, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Master shutting down.")
        finally:
            server.close()

    def handle_connection(self, sock, addr):
        f = sock.makefile('r', encoding='utf-8')
        try:
            line = f.readline()
            if not line:
                return
            msg = json.loads(line)
            role = msg.get('role')
            
            if role == 'worker':
                self.handle_worker(sock, f, addr)
            elif role == 'client':
                self.handle_client(sock, f, msg, addr)
            else:
                print(f"Unknown role from {addr}")
        except Exception as e:
            print(f"Error handling connection from {addr}: {e}")
        finally:
            sock.close()

    def handle_worker(self, sock, f, addr):
        print(f"Worker connected from {addr}")
        with self.workers_lock:
            self.workers[sock] = {'lock': threading.Lock(), 'f': f, 'sock': sock}
            
        try:
            while True:
                line = f.readline()
                if not line:
                    break
                response = json.loads(line)
                job_id = response.get('job_id')
                results = response.get('results', [])
                
                if job_id in self.job_results:
                    self.job_results[job_id].extend(results)
                    self.job_expected[job_id] -= 1
                    if self.job_expected[job_id] <= 0:
                        self.job_locks[job_id].set()
        except Exception as e:
            pass
            # print(f"Worker {addr} disconnected: {e}")
        finally:
            print(f"Worker disconnected from {addr}")
            with self.workers_lock:
                if sock in self.workers:
                    del self.workers[sock]

    def handle_client(self, sock, f, msg, addr):
        print(f"Client request received: {msg}")
        target_name = msg.get('target_name')
        threshold = msg.get('threshold', 0.5)
        chunk_size = msg.get('chunk_size', 10000)
        
        if not target_name:
            self.send_json(sock, {'error': 'Missing target_name'})
            return
            
        with self.workers_lock:
            active_workers = list(self.workers.values())
            
        if not active_workers:
            self.send_json(sock, {'error': 'No workers available'})
            return
            
        start_time = time.time()
        job_id = str(uuid.uuid4())
        
        # Determine chunks
        chunks = [self.data[i:i + chunk_size] for i in range(0, len(self.data), chunk_size)]
        
        self.job_results[job_id] = []
        self.job_expected[job_id] = len(chunks)
        self.job_locks[job_id] = threading.Event()
        
        # Distribute chunks round robin
        worker_idx = 0
        for chunk in chunks:
            worker = active_workers[worker_idx % len(active_workers)]
            worker_idx += 1
            
            task = {
                'job_id': job_id,
                'target_name': target_name,
                'threshold': threshold,
                'data': chunk
            }
            with worker['lock']:
                try:
                    worker['sock'].sendall((json.dumps(task) + '\n').encode('utf-8'))
                except:
                    # If send fails, this chunk is lost in this simple implementation
                    # A robust one would re-queue it. For now, we decrement expected.
                    self.job_expected[job_id] -= 1
                    pass

        # Wait for all chunks
        self.job_locks[job_id].wait()
        
        end_time = time.time()
        duration = end_time - start_time
        
        results = self.job_results[job_id]
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        response = {
            'duration': duration,
            'matches': len(results),
            'results': results[:100] # return top 100 to avoid huge payload
        }
        
        self.send_json(sock, response)
        
        # cleanup
        del self.job_results[job_id]
        del self.job_expected[job_id]
        del self.job_locks[job_id]

    def send_json(self, sock, data):
        try:
            sock.sendall((json.dumps(data) + '\n').encode('utf-8'))
        except:
            pass

if __name__ == "__main__":
    import sys
    data_file = "names.txt"
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    master = MasterNode(data_file)
    master.start()
