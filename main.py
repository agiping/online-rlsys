import logging
import uuid
import os

from online_rl_agent.agent.agent import DevOpsAgent
from online_rl_agent.chaos.injector import apply_chaos_experiment
from online_rl_agent.user_agent.simulator import get_user_task, get_reward_from_user
from online_rl_agent.data.trajectory_store import TrajectoryStore

# Try to import config, but provide guidance if it's missing.
try:
    from online_rl_agent import config
except ImportError:
    print("="*50)
    print("ERROR: Configuration file not found.")
    print("Please copy 'online_rl_agent/config.py.example' to 'online_rl_agent/config.py'")
    print("and fill in your DEEPSEEK_API_KEY.")
    print("="*50)
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainLoop")

def main_loop():
    """
    The main loop for the online RL agent system.
    """
    logger.info("Initializing DevOps Agent and Trajectory Store...")
    
    # Validate API key before starting
    if not hasattr(config, 'DEEPSEEK_API_KEY') or "YOUR_DEEPSEEK_API_KEY" in config.DEEPSEEK_API_KEY:
        logger.error("DeepSeek API key is not configured correctly in online_rl_agent/config.py")
        return
        
    agent = DevOpsAgent(api_key=config.DEEPSEEK_API_KEY, model="deepseek-coder")
    store = TrajectoryStore(save_path='data/trajectories.jsonl')
    
    # Determine chaos template path
    chaos_template_path = os.path.join(os.path.dirname(__file__), 'online_rl_agent', 'chaos', 'templates', 'pod-failure.yaml')

    while True:
        logger.info("--- Starting New Episode ---")
        
        # 1. Inject fault
        logger.info("Please manually inject a fault into the cluster.")
        logger.info(f"You can use the example chaos experiment: kubectl apply -f {chaos_template_path}")
        input("Press Enter after you have injected the fault and it has taken effect...")
        # In a future version, this could be automated:
        # apply_chaos_experiment(chaos_template_path)

        # 2. Get user task
        user_task = get_user_task()
        logger.info(f"Received user task: {user_task}")

        # 3. Start trajectory
        trajectory_id = f"traj_{uuid.uuid4()}"
        store.start_new_trajectory(trajectory_id)

        # 4. Run agent
        logger.info("Running DevOps Agent to solve the problem...")
        final_answer = agent.run(user_task, trajectory_store=store)

        # 5. Get reward
        reward = get_reward_from_user(final_answer)
        logger.info(f"Received reward: {reward}")

        # 6. End and save trajectory
        store.end_trajectory(reward)
        store.save_trajectory()
        
        logger.info(f"Episode finished. Trajectory {trajectory_id} saved.")

        # 7. Ask to continue
        continue_choice = input("Start another episode? (y/n): ").lower()
        if continue_choice != 'y':
            logger.info("Exiting.")
            break

if __name__ == "__main__":
    main_loop()
