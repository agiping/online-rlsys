import json
import logging
import os
import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrajectoryStore:
    def __init__(self, save_path: str = 'data/trajectories.json'):
        """
        Initializes the TrajectoryStore.

        Args:
            save_path: The file path where trajectories will be saved.
        """
        self.save_path = save_path
        self.current_trajectory = {
            "id": None,
            "start_time": None,
            "end_time": None,
            "steps": [],
            "reward": None
        }
        self._ensure_data_directory_exists()

    def _ensure_data_directory_exists(self):
        """Ensures the directory for the save_path exists."""
        dir_name = os.path.dirname(self.save_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logging.info(f"Created data directory: {dir_name}")

    def start_new_trajectory(self, trajectory_id: str):
        """
        Resets and starts a new trajectory.
        """
        self.current_trajectory = {
            "id": trajectory_id,
            "start_time": datetime.datetime.utcnow().isoformat(),
            "end_time": None,
            "steps": [],
            "reward": None
        }
        logging.info(f"Started new trajectory with ID: {trajectory_id}")

    def add_step(self, thought: str, tool_name: str, tool_args: Dict, tool_output: str):
        """

        Adds a single step of interaction to the current trajectory.
        """
        if not self.current_trajectory["id"]:
            logging.warning("Cannot add step: No trajectory has been started.")
            return

        step_data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "thought": thought,
            "action": {
                "tool_name": tool_name,
                "tool_args": tool_args
            },
            "observation": tool_output
        }
        self.current_trajectory["steps"].append(step_data)
        
    def add_final_answer(self, final_answer: str):
        """
        Adds the agent's final answer as the last step.
        """
        self.add_step(
            thought="This is the final step, providing the answer.",
            tool_name="final_answer",
            tool_args={"answer": final_answer},
            tool_output="" # No observation for the final answer
        )

    def end_trajectory(self, reward: int):
        """
        Adds the final reward and marks the trajectory as complete.
        """
        if not self.current_trajectory["id"]:
            logging.warning("Cannot end trajectory: No trajectory has been started.")
            return
        
        self.current_trajectory["reward"] = reward
        self.current_trajectory["end_time"] = datetime.datetime.utcnow().isoformat()
        logging.info(f"Ending trajectory {self.current_trajectory['id']} with reward: {reward}")


    def save_trajectory(self):
        """
        Saves the completed trajectory to the specified JSON file.
        Each trajectory is saved as a new line in the JSONL format.
        """
        if not self.current_trajectory.get("reward"):
            logging.warning("Cannot save: Trajectory is not yet complete (reward is missing).")
            return
            
        try:
            with open(self.save_path, 'a') as f:
                f.write(json.dumps(self.current_trajectory) + '\n')
            logging.info(f"Successfully saved trajectory to {self.save_path}")
        except IOError as e:
            logging.error(f"Failed to save trajectory to {self.save_path}: {e}")

if __name__ == '__main__':
    # Example usage
    store = TrajectoryStore(save_path='data/test_trajectories.jsonl')
    
    # Start a new trajectory
    store.start_new_trajectory("test-run-001")
    
    # Add a few steps
    store.add_step(
        thought="First, I will check the pods.",
        tool_name="get_pods",
        tool_args={"namespace": "default"},
        tool_output="pod-a is running, pod-b is CrashLoopBackOff"
    )
    store.add_step(
        thought="Pod-b looks suspicious. I will check its logs.",
        tool_name="get_pod_logs",
        tool_args={"pod_name": "pod-b", "namespace": "default"},
        tool_output="Error: Database connection failed."
    )
    store.add_final_answer("The problem is a database connection error in pod-b.")
    
    # End the trajectory with a reward
    store.end_trajectory(reward=1)
    
    # Save it
    store.save_trajectory()

    print(f"\nTrajectory saved to {store.save_path}. Check the file content.")
    # Clean up the test file
    # os.remove(store.save_path)
