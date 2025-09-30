import os
import logging
from .base import BaseEnvironment
from online_rl_agent.chaos.injector import apply_chaos_experiment, delete_chaos_experiment

class KubernetesChaosEnvironment(BaseEnvironment):
    """
    A specific implementation of the environment for a Kubernetes cluster
    where faults are injected using Chaos Mesh.
    """
    def __init__(self, chaos_yaml_path: str):
        """
        Initializes the Kubernetes environment.

        Args:
            chaos_yaml_path: The path to the Chaos Mesh experiment YAML.
        """
        self.chaos_yaml_path = chaos_yaml_path
        if not os.path.exists(self.chaos_yaml_path):
            raise FileNotFoundError(f"Chaos experiment YAML not found at: {self.chaos_yaml_path}")
        logging.info(f"KubernetesChaosEnvironment initialized with chaos template: {self.chaos_yaml_path}")

    def setup(self):
        """
        Applies the chaos experiment to the cluster.
        """
        logging.info("Setting up Kubernetes environment by applying chaos experiment...")
        apply_chaos_experiment(self.chaos_yaml_path)

    def get_task(self) -> str:
        """
        Returns the hardcoded task for the Kubernetes troubleshooting scenario.
        """
        return "My service is down, please investigate and find the root cause."

    def cleanup(self):
        """
        Deletes the chaos experiment from the cluster.
        """
        logging.info("Cleaning up Kubernetes environment by deleting chaos experiment...")
        delete_chaos_experiment(self.chaos_yaml_path)
