import socket
import json
import argparse
import time

HOST = '127.0.0.1'
PORT = 5000

def send_request(target_name, threshold, chunk_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Could not connect to master at {HOST}:{PORT}")
        return
        
    request = {
        'role': 'client',
        'target_name': target_name,
        'threshold': threshold,
        'chunk_size': chunk_size
    }
    
    sock.sendall((json.dumps(request) + '\n').encode('utf-8'))
    
    f = sock.makefile('r', encoding='utf-8')
    line = f.readline()
    if line:
        response = json.loads(line)
        if 'error' in response:
            print(f"Error: {response['error']}")
        else:
            print(f"Found {response['matches']} matches in {response['duration']:.4f} seconds.")
            print(f"Top matches:")
            for name, sim in response['results'][:10]:
                print(f"  {name}: {sim:.4f}")
    
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Jaccard Similarity Distributed Search Client')
    parser.add_argument('--target', type=str, required=True, help='Name to search for')
    parser.add_argument('--threshold', type=float, default=0.5, help='Similarity threshold (0.0 - 1.0)')
    parser.add_argument('--chunk-size', type=int, default=10000, help='Chunk size for distribution')
    
    args = parser.parse_args()
    send_request(args.target, args.threshold, args.chunk_size)
