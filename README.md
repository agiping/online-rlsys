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


我们来讨论一个 idea：我希望用在线强化学习的思路，训练一个集群运维的 Agent。思路如下：

1. 在批量创建的 kind 集群中，部署模拟业务，然后用 chaos-mesh 等工具，注入故障，并用一个模拟用户的进程，来向大模型Agent 提问，比如“我的服务为什么挂了?”;
2. Agent 收到问题后，调用工具研究根因，比如查看 log，发现根因是 “资源不足” 后，调用工具进行修复，比如调到服务的资源配置；
3. observer 进程观察用户的问题是否被解决，若解决，则 Reward 为 1，若没有解决，则 Reward 为 0，若 Agent 导致了更严重的问题，则 Reward 为-1

通过这样的持续训练，让 Agent 自己学会如何运维集群，Agent 的强化训练将 grounded on the truth；

经过这样的第一阶段训练之后，也就是说在我们模拟的故障上（虽然是模拟，但也是真实的故障）；Agent 将部署到线上，在线上，Agent 将是一种 Online 的RL 训练方式：

1. Serving is Training，Agent 在解决实际的集群运维问题的过程中，表现可能好，也可能坏（我们预期经过上面的第一阶段的训练，Agent 的表现假设还可以），那么这些线上实际 Serving 产生的轨迹数据，包括问题是否被成功解决的标记信号，将被保存下来，并定期对模型在线进行训练；
2. 每训练完一个版本后，比如 Agent Serving 了 6 小时为一个周期，这 6 小时的数据将更新一版本参数，然后通过 evaluation，如果评估通过，这一版本的参数将被更新为正式 Serving 的版本，如果交替循环。

上面是所有 Two-stage Online Agentic RL 的大致思路。按照当前 LLM，Agent，RL 的发展进度，我觉得技术上是可行的。但确实也面临很多问题：

1. 环境是动态持续变化的，observer 如何观察（观察方式、频率、以及和模拟用户的关系），并如何根据观察的结果来判定 Reward？
2. 第一阶段貌似可以用 GRPO 等算法来训练，但第二阶段肯定不行，真实的某个线上问题不可能被反复采样好几次来支持训练，第一第二阶段的 RL 算法不同会有什么问题？
3. 第一阶段我可以用当前分离式的 RL 框架直接训练，无非是交互的环境从主流的 code、math 变成了一个个的 k8s 集群；但第二阶段如何设计训练框架？第二阶段有好几个问题需要考虑：
3.1 成本问题：之前部署 Agent，只需要后面接一个推理实例的 API，Agent 本身的 workflow 可能就是一个 CPU 任务跑在集群中就可以，比较简单，但现在还需要支持在线训练，需要引入训练资源；
3.2 上线后，由于 Agent 要持续服务，智能运维服务不能中断，所以框架要支持多版本推理？然后交替进行迭代，框架设计层面如何做，如何与第一阶段的框架保持一致（同一个框架）？
4. 其实集群运维只是我探索在线强化学习的一个特定场景，我更想通过这个过程，构建一个专门用于在线强化的框架。比如以后的大模型应用的推理集群都是自动、动态学习并定期更新权重的，背后的第一性原理是，Agent 在 Serving 过程中的 experience 数据包含对世界的经验知识，通过在线强化学习，能持续、高效率的实现 self-envole。面向这个目标，我如何与运维场景的框架设计在结构上具有一致性、扩展性？比如考虑 chat 类应用，如何与做 Serving 的 k8s 集群本身协同、如何处理当前主流 RL 框架中普遍用的 ray 的关系？训推资源怎么安排，权重具体怎么更新。