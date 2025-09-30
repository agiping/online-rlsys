# Online RL System for DevOps Agent

This project is an MVP for building an online reinforcement learning system to train a DevOps agent. The agent learns to diagnose and solve problems in a Kubernetes cluster by interacting with it, receiving feedback, and continuously improving its policy.

## Project Goal

The primary goal is to create a closed-loop system where:
1.  A fault is injected into a Kubernetes cluster (using Chaos Mesh).
2.  A user-agent reports a generic problem (e.g., "my service is down").
3.  The DevOps agent uses a set of tools (`kubectl` wrappers) to investigate the cluster state.
4.  The agent proposes a solution based on its observations.
5.  The user-agent provides a reward (1 for success, 0 for failure).
6.  The `(state, action, reward)` trajectory is stored for future training.

## Getting Started

### Prerequisites

- A running Kubernetes cluster (e.g., Kind, Minikube).
- `kubectl` configured to connect to your cluster.
- Chaos Mesh installed in your cluster.
- Python 3.8+

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd online-rlsys
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    - Rename `online_rl_agent/config.py.example` to `online_rl_agent/config.py`.
    - Open `online_rl_agent/config.py` and add your DeepSeek API key.

### Running the MVP

(Instructions to be added once the main script is complete)
