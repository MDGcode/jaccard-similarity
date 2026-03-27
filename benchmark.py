import subprocess
import time
import sys
import os
import signal

def run_tests():
    print("Generating data file (1,000,000 records for fast testing)...")
    subprocess.run([sys.executable, "generate_data.py", "1000000", "0.8"])

    print("\n--- Starting Master ---")
    master_process = subprocess.Popen([sys.executable, "master.py", "names.txt"])
    time.sleep(2) # Give it time to load data
    
    workers = []
    
    # helper
    def start_workers(n):
        for _ in range(n):
            p = subprocess.Popen([sys.executable, "worker.py"])
            workers.append(p)
        time.sleep(1) # Wait for connect
        
    def stop_workers():
        for p in workers:
            p.terminate()
            p.wait()
        workers.clear()
        
    try:
        print("\n--- Analyzing Speedup (Varying Number of Workers) ---")
        chunk_size = 50000
        target = "Ion"
        
        for w_cnt in [1, 2, 4]:
            print(f"\nTesting with {w_cnt} workers...")
            start_workers(w_cnt)
            
            # Send client request
            client_proc = subprocess.run([
                sys.executable, "client.py", 
                "--target", target, 
                "--threshold", "0.2", 
                "--chunk-size", str(chunk_size)
            ], capture_output=True, text=True)
            
            print(client_proc.stdout)
            
            stop_workers()

        print("\n--- Analyzing Throughput (Varying Chunk Size) ---")
        start_workers(4) # 4 workers
        
        for chk_sz in [10000, 25000, 50000, 100000]:
            print(f"\nTesting with chunk_size {chk_sz}...")
            
            # Send client request
            client_proc = subprocess.run([
                sys.executable, "client.py", 
                "--target", target, 
                "--threshold", "0.2", 
                "--chunk-size", str(chk_sz)
            ], capture_output=True, text=True)
            
            for line in client_proc.stdout.split("\n"):
                if "Found" in line or "duration" in line:
                    print(line)
        
        stop_workers()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        master_process.terminate()
        master_process.wait()
        stop_workers()
        print("\nTests complete.")

if __name__ == "__main__":
    run_tests()
