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

1. No persistent storage
2. Simple state model (single string value)
3. Basic network partition handling
4. No log replication
5. No dynamic membership changes
6. Runs only on localhost

## Example Session

```bash
# Terminal 1
$ python raft.py 8000
Node 8000 starting election for term 1
Node 8000 elected as leader for term 1

# Terminal 2
$ python raft.py 8001
Node 8001 updated value to: some_value

# Terminal 1
> set some_value
Leader 8000 setting value to: some_value
```

## Error Handling

- Graceful shutdown with Ctrl+C
- Automatic recovery from leader failures
- Basic network error handling

## Contributing

Feel free to improve this implementation by addressing any of the limitations mentioned above or adding new features like:
- Persistent storage
- Full log replication
- Configuration changes
- Network partition handling
- Log compaction