import socket
import threading
import time
import random
import json
import sys
import signal

class RaftNode:
    def __init__(self, node_id, peers):
        self.id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.state = "follower"
        self.leader_id = None
        self.current_value = ""  # The current state/value
        
        # Timing constants
        self.HEARTBEAT_TIMEOUT = 1.0
        self.ELECTION_TIMEOUT_BASE = 2.0
        
        # Reset election timeout
        self.reset_election_timeout()
        
        # Setup networking
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(("localhost", self.id))
        
        # Start main thread
        self.running = True
        threading.Thread(target=self.run).start()
        threading.Thread(target=self.receive_messages).start()

    def reset_election_timeout(self):
        self.last_heartbeat = time.time()
        self.election_timeout = self.ELECTION_TIMEOUT_BASE + random.uniform(0, 1)

    def run(self):
        while self.running:
            if self.state == "follower" or self.state == "candidate":
                if time.time() - self.last_heartbeat > self.election_timeout:
                    self.start_election()
            elif self.state == "leader":
                self.send_heartbeat()
                time.sleep(self.HEARTBEAT_TIMEOUT)
            time.sleep(0.1)

    def start_election(self):
        self.state = "candidate"
        self.current_term += 1
        self.voted_for = self.id
        self.votes_received = 1
        print(f"Node {self.id} starting election for term {self.current_term}")
        
        # Request votes from all peers
        message = {
            "type": "request_vote",
            "term": self.current_term,
            "candidate_id": self.id,
        }
        self.broadcast_message(message)
        self.reset_election_timeout()

    def send_heartbeat(self):
        message = {
            "type": "append_entries",
            "term": self.current_term,
            "leader_id": self.id,
            "value": self.current_value
        }
        self.broadcast_message(message)

    def broadcast_message(self, message):
        for peer in self.peers:
            try:
                self.server_socket.sendto(json.dumps(message).encode(), ("localhost", peer))
            except:
                pass

    def receive_messages(self):
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                message = json.loads(data.decode())
                self.handle_message(message)
            except:
                continue

    def handle_message(self, message):
        if message["term"] > self.current_term:
            self.current_term = message["term"]
            self.state = "follower"
            self.voted_for = None
            
        if message["type"] == "request_vote":
            self.handle_vote_request(message)
        elif message["type"] == "vote_response":
            self.handle_vote_response(message)
        elif message["type"] == "append_entries":
            self.handle_append_entries(message)
        elif message["type"] == "set_value":
            self.handle_set_value(message)

    def handle_vote_request(self, message):
        if (message["term"] >= self.current_term and 
            (self.voted_for is None or self.voted_for == message["candidate_id"])):
            self.voted_for = message["candidate_id"]
            response = {
                "type": "vote_response",
                "term": self.current_term,
                "vote_granted": True
            }
            self.server_socket.sendto(json.dumps(response).encode(), ("localhost", message["candidate_id"]))

    def handle_vote_response(self, message):
        if self.state == "candidate" and message.get("vote_granted"):
            self.votes_received += 1
            if self.votes_received > len(self.peers) / 2:
                print(f"Node {self.id} elected as leader for term {self.current_term}")
                self.state = "leader"
                self.leader_id = self.id

    def handle_append_entries(self, message):
        self.reset_election_timeout()
        if message["term"] >= self.current_term:
            self.state = "follower"
            self.leader_id = message["leader_id"]
            if self.current_value != message["value"]:  # Only print if value actually changes
                self.current_value = message["value"]
                print(f"Node {self.id} updated value to: {self.current_value}")

    def handle_set_value(self, message):
        if self.state == "leader":
            self.current_value = message["value"]
            print(f"Leader {self.id} setting value to: {self.current_value}")
            self.send_heartbeat()

    def shutdown(self):
        self.running = False
        self.server_socket.close()


def run_node(node_id, peer_ids):
    peers = [pid for pid in peer_ids if pid != node_id]
    node = RaftNode(node_id, peers)
    
    def signal_handler(sig, frame):
        print(f"\nShutting down node {node_id}")
        node.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Simple CLI for setting values
    while True:
        try:
            command = input()
            if command.startswith("set "):
                value = command[4:]
                if node.state == "leader":
                    node.handle_set_value({"value": value})
                else:
                    print(f"Not the leader. Current leader is node {node.leader_id}")
        except EOFError:
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python raft.py <node_id>")
        sys.exit(1)
    
    node_id = int(sys.argv[1])
    peer_ids = [8000, 8001, 8002]  # Fixed ports for simplicity
    run_node(node_id, peer_ids)
