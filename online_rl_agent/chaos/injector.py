import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def apply_chaos_experiment(yaml_path: str) -> bool:
    """
    Applies a Chaos Mesh experiment YAML to the cluster.

    Args:
        yaml_path: The relative path to the Chaos Mesh experiment YAML file.

    Returns:
        True if the command was successful, False otherwise.
    """
    if not os.path.exists(yaml_path):
        logging.error(f"Chaos experiment YAML not found at: {yaml_path}")
        return False

    command = ["kubectl", "apply", "-f", yaml_path]
    try:
        logging.info(f"Applying chaos experiment: {' '.join(command)}")
        # We use check=True to raise an exception on non-zero exit codes.
        subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info("Successfully applied chaos experiment.")
        return True
    except FileNotFoundError:
        logging.error("`kubectl` command not found. Please ensure it is installed and in your PATH.")
        return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to apply chaos experiment. Return code: {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        return False

if __name__ == '__main__':
    # This assumes the script is run from the root of the project.
    # For a real run, the main.py script will handle pathing.
    # You need to have a target application running for this to have an effect.
    
    # Construct the path relative to this script's location
    # injector.py -> chaos/ -> online_rl_agent/ -> online-rlsys/
    script_dir = os.path.dirname(__file__)
    template_path = os.path.join(script_dir, 'templates', 'pod-failure.yaml')

    print("--- Applying a sample pod-failure chaos experiment ---")
    # You would need to edit the pod-failure.yaml to target a real pod in your cluster.
    print(f"Note: Ensure the YAML at '{template_path}' targets a running pod in your cluster.")
    
    # apply_chaos_experiment(template_path)
    print("\nTo run this for real, uncomment the line above and configure the YAML file.")
