import logging
import uuid
import os
import time

from online_rl_agent.agent.agent import DevOpsAgent
from online_rl_agent.user_agent.simulator import get_reward_from_user
from online_rl_agent.data.trajectory_store import TrajectoryStore
from online_rl_agent.environment.k8s_chaos_env import KubernetesChaosEnvironment

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
    logger.info("Initializing DevOps Agent, Environment, and Trajectory Store...")
    
    # Validate API key before starting
    if not hasattr(config, 'DEEPSEEK_API_KEY') or "YOUR_DEEPSEEK_API_KEY" in config.DEEPSEEK_API_KEY:
        logger.error("DeepSeek API key is not configured correctly in online_rl_agent/config.py")
        return
        
    # --- Initialization ---
    agent = DevOpsAgent(api_key=config.DEEPSEEK_API_KEY, model="deepseek-coder")
    store = TrajectoryStore(save_path='data/trajectories.jsonl')
    
    # The main loop now only interacts with the Environment abstraction
    chaos_template_path = os.path.join(os.path.dirname(__file__), 'online_rl_agent', 'chaos', 'templates', 'pod-failure.yaml')
    env = KubernetesChaosEnvironment(chaos_yaml_path=chaos_template_path)

    while True:
        logger.info("--- Starting New Episode ---")
        
        try:
            # 1. Setup environment
            env.setup()
            logger.info("Environment setup complete. Waiting for 15 seconds for fault to stabilize...")
            time.sleep(15)

            # 2. Get user task from the environment
            user_task = env.get_task()
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

        finally:
            # 7. Cleanup environment, ensuring it runs even if the agent fails
            env.cleanup()
            logger.info("Environment cleanup complete.")

        # 8. Ask to continue
        continue_choice = input("Start another episode? (y/n): ").lower()
        if continue_choice != 'y':
            logger.info("Exiting.")
            break

if __name__ == "__main__":
    main_loop()
