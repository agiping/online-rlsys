import logging
import uuid
import os
import time
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from online_rl_agent.agent.agent import DevOpsAgent
from online_rl_agent.user_agent.simulator import get_reward_from_user
from online_rl_agent.data.trajectory_store import TrajectoryStore
from online_rl_agent.environment.k8s_chaos_env import KubernetesChaosEnvironment
from online_rl_agent.sandbox.kind_sandbox import KindSandbox

# Try to import config
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
logger = logging.getLogger("SandboxRunner")

def main():
    logger.info("Initializing Sandbox Environment...")

    # Validate API key
    if not hasattr(config, 'DEEPSEEK_API_KEY') or "YOUR_DEEPSEEK_API_KEY" in config.DEEPSEEK_API_KEY:
        logger.error("DeepSeek API key is not configured correctly in online_rl_agent/config.py")
        return

    # 1. Start Sandbox
    sandbox = KindSandbox(cluster_name="rl-agent-sandbox")
    try:
        sandbox.start()
        access_config = sandbox.get_access_config()
        kubeconfig_path = access_config['kubeconfig']
        logger.info(f"Sandbox started. Kubeconfig: {kubeconfig_path}")

        # 2. Initialize Agent and Environment with sandbox kubeconfig
        agent = DevOpsAgent(
            api_key=config.DEEPSEEK_API_KEY, 
            model="deepseek-coder",
            kubeconfig=kubeconfig_path
        )
        store = TrajectoryStore(save_path='data/trajectories.jsonl')
        
        chaos_template_path = os.path.join(
            os.path.dirname(__file__), 
            'online_rl_agent', 'chaos', 'templates', 'pod-failure.yaml'
        )
        env = KubernetesChaosEnvironment(
            chaos_yaml_path=chaos_template_path,
            kubeconfig=kubeconfig_path
        )

        while True:
            logger.info("--- Starting New Episode in Sandbox ---")
            
            try:
                # 3. Setup environment (Chaos)
                env.setup()
                logger.info("Environment setup complete. Waiting for 15 seconds for fault to stabilize...")
                time.sleep(15)

                # 4. Get task
                user_task = env.get_task()
                logger.info(f"Received user task: {user_task}")

                # 5. Start trajectory
                trajectory_id = f"traj_{uuid.uuid4()}"
                store.start_new_trajectory(trajectory_id)

                # 6. Run agent
                logger.info("Running DevOps Agent...")
                final_answer = agent.run(user_task, trajectory_store=store)

                # 7. Get reward
                reward = get_reward_from_user(final_answer)
                logger.info(f"Received reward: {reward}")

                # 8. Save
                store.end_trajectory(reward)
                store.save_trajectory()
                
                logger.info(f"Episode finished. Trajectory {trajectory_id} saved.")

            except Exception as e:
                logger.error(f"An error occurred during the episode: {e}", exc_info=True)
            finally:
                # 9. Cleanup Chaos
                env.cleanup()
                logger.info("Episode cleanup complete.")

            # 10. Ask to continue
            continue_choice = input("Start another episode? (y/n): ").lower()
            if continue_choice != 'y':
                logger.info("Exiting loop.")
                break

    except Exception as e:
        logger.error(f"Sandbox initialization failed: {e}", exc_info=True)
    finally:
        # 11. Teardown Sandbox
        logger.info("Tearing down sandbox...")
        sandbox.stop()
        logger.info("Sandbox teardown complete.")

if __name__ == "__main__":
    main()




