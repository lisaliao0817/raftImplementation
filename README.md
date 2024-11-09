# Raft Consensus Protocol Implementation

A simplified implementation of the Raft consensus protocol in Python, demonstrating leader election and basic state replication.

## Features

- Leader election following Raft protocol
- Basic state replication
- Heartbeat mechanism
- Fault tolerance (handles leader crashes)
- Simple command-line interface for state updates

## Requirements

- Python 3.6+
- Standard Python libraries (no additional installations needed)

## Usage

1. Open three terminal windows to simulate a three-node cluster
2. Run each node on a different port:

```bash
python raft.py 8000
python raft.py 8001
python raft.py 8002
```

### Commands

- `set <value>`: Set a new value (only works when sent to the leader)
- `Ctrl+C`: Gracefully shutdown a node

## How It Works

### Node States
- **Follower**: Default state, receives updates from leader
- **Candidate**: Temporary state during election
- **Leader**: Coordinates all changes, sends heartbeats

### Key Mechanisms

1. **Leader Election**
   - Followers become candidates if no heartbeat received
   - Candidates request votes from peers
   - Winner becomes leader for the term

2. **State Replication**
   - Only leader accepts state changes
   - Changes propagated via heartbeats
   - Followers confirm updates

3. **Fault Tolerance**
   - Automatic leader election on failure
   - Consistent state maintained across nodes

## Implementation Details

The core implementation is in the `RaftNode` class (lines 9-142), which handles:
- Network communication
- State management
- Election process
- Value replication

## Limitations

1. **No persistent storage**
   - All state is held in memory and lost when nodes restart
   - In a production system, the log and state should be written to disk
   - Critical for recovering from crashes and maintaining data durability

2. **Simple state model (single string value)**
   - Current implementation only maintains a single string value
   - Real distributed systems typically need to handle complex data structures
   - No support for multiple concurrent operations or transactions

3. **Basic network partition handling**
   - Network failures are handled through simple timeouts
   - No sophisticated partition detection or resolution
   - Split-brain scenarios (where multiple leaders could emerge) are possible

4. **No log replication**
   - Only replicates current state, not the sequence of changes
   - Missing key Raft feature of maintaining ordered operation log
   - Cannot replay history or handle inconsistencies properly

5. **No dynamic membership changes**
   - Cluster membership is static and defined at startup
   - No way to add or remove nodes while the system is running
   - Configuration changes require full system restart

6. **Runs only on localhost**
   - Limited to running all nodes on a single machine
   - Uses simple UDP communication on localhost
   - Not suitable for real distributed deployment across network

## Example Session

```bash
# Terminal 1
$ python raft.py 8000
Node 8000 starting election for term 1

# Terminal 2
$ python raft.py 8001

# Terminal 1
Node 8000 elected as leader for term 1
> set some_value
Leader 8000 setting value to: some_value

# Terminal 2
Node 8001 updated value to: some_value
```

## AI Usage
I used ChatGPT4o first but its implementation was buggy and it could not really fix its own bugs so I used claude-3.5-sonnet that was embedded in Cursor, an IDE I just started using. It produced the code and also improved it based on the feedback I gave. 