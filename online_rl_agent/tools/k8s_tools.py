import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _run_kubectl_command(command: list[str]) -> str:
    """
    A helper function to run a kubectl command and return the output.
    
    Args:
        command: A list of strings representing the command to run.
        
    Returns:
        The stdout of the command as a string.
        
    Raises:
        subprocess.CalledProcessError: If the command returns a non-zero exit code.
    """
    try:
        logging.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except FileNotFoundError:
        logging.error("`kubectl` command not found. Please ensure it is installed and in your PATH.")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}: {e.stderr}")
        return e.stderr

def get_pods(namespace: str = "default") -> str:
    """
    Gets the list of pods in a specified namespace.
    
    Args:
        namespace: The Kubernetes namespace to query.
        
    Returns:
        A string containing the kubectl output for getting pods.
    """
    command = ["kubectl", "get", "pods", "-n", namespace]
    return _run_kubectl_command(command)

def describe_pod(pod_name: str, namespace: str = "default") -> str:
    """
    Describes a specific pod in a specified namespace.
    
    Args:
        pod_name: The name of the pod to describe.
        namespace: The Kubernetes namespace where the pod resides.
        
    Returns:
        A string containing the kubectl output for describing the pod.
    """
    if not pod_name:
        return "Error: pod_name cannot be empty."
    command = ["kubectl", "describe", "pod", pod_name, "-n", namespace]
    return _run_kubectl_command(command)

def get_pod_logs(pod_name: str, namespace: str = "default", tail: int = 50) -> str:
    """
    Gets the logs of a specific pod in a specified namespace.
    
    Args:
        pod_name: The name of the pod to get logs from.
        namespace: The Kubernetes namespace where the pod resides.
        tail: The number of recent lines to display.
        
    Returns:
        A string containing the kubectl output for the pod's logs.
    """
    if not pod_name:
        return "Error: pod_name cannot be empty."
    command = ["kubectl", "logs", pod_name, "-n", namespace, f"--tail={tail}"]
    return _run_kubectl_command(command)

if __name__ == '__main__':
    # Example usage for manual testing
    print("--- Getting all pods in default namespace ---")
    print(get_pods())
    
    # To test describe and logs, you'll need a pod name.
    # Replace 'your-pod-name' with a real pod name from your cluster.
    # pod_name_to_test = "your-pod-name" 
    # if pod_name_to_test != "your-pod-name":
    #     print(f"--- Describing pod: {pod_name_to_test} ---")
    #     print(describe_pod(pod_name_to_test))
        
    #     print(f"--- Getting logs for pod: {pod_name_to_test} ---")
    #     print(get_pod_logs(pod_name_to_test))
