import subprocess
import os
import logging
import time
from typing import Dict, Any, Optional
from .base import Sandbox

class KindSandbox(Sandbox):
    def __init__(self, cluster_name: str = "kind-sandbox", kubeconfig_path: Optional[str] = None):
        self.cluster_name = cluster_name
        # Use a specific kubeconfig file for this sandbox to avoid messing with default ~/.kube/config
        # If not provided, create one in the current directory
        self.kubeconfig_path = kubeconfig_path or os.path.abspath(f"{self.cluster_name}-kubeconfig")
        self.logger = logging.getLogger(__name__)

    def _check_kind_installed(self):
        try:
            subprocess.run(["kind", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("kind is not installed or not in PATH. Please install kind.")

    def _check_kubectl_installed(self):
        try:
            subprocess.run(["kubectl", "version", "--client"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("kubectl is not installed or not in PATH. Please install kubectl.")

    def start(self) -> None:
        self._check_kind_installed()
        self._check_kubectl_installed()

        self.logger.info(f"Starting Kind cluster '{self.cluster_name}'...")
        
        # Check if cluster already exists
        result = subprocess.run(["kind", "get", "clusters"], capture_output=True, text=True)
        if self.cluster_name in result.stdout.splitlines():
            self.logger.info(f"Cluster '{self.cluster_name}' already exists. Reusing it.")
            # If it exists, we need to export the kubeconfig again in case the file is missing
            try:
                cmd = ["kind", "get", "kubeconfig", "--name", self.cluster_name]
                with open(self.kubeconfig_path, "w") as f:
                    subprocess.run(cmd, stdout=f, check=True)
            except subprocess.CalledProcessError as e:
                 self.logger.error(f"Failed to retrieve kubeconfig for existing cluster: {e}")
                 raise
        else:
            try:
                cmd = [
                    "kind", "create", "cluster", 
                    "--name", self.cluster_name,
                    "--kubeconfig", self.kubeconfig_path
                ]
                subprocess.run(cmd, check=True)
                self.logger.info(f"Cluster '{self.cluster_name}' created successfully.")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to create Kind cluster: {e}")
                raise

        # Verify connection
        self._wait_for_ready()

    def _wait_for_ready(self, timeout: int = 120):
        self.logger.info("Waiting for cluster to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if nodes are ready
                subprocess.run(
                    ["kubectl", "--kubeconfig", self.kubeconfig_path, "get", "nodes"], 
                    check=True, capture_output=True
                )
                self.logger.info("Cluster is ready.")
                return
            except subprocess.CalledProcessError:
                time.sleep(5)
        raise RuntimeError("Timed out waiting for cluster to be ready.")

    def stop(self) -> None:
        self.logger.info(f"Stopping Kind cluster '{self.cluster_name}'...")
        try:
            subprocess.run(["kind", "delete", "cluster", "--name", self.cluster_name], check=True)
            # Clean up kubeconfig file
            if os.path.exists(self.kubeconfig_path):
                os.remove(self.kubeconfig_path)
            self.logger.info(f"Cluster '{self.cluster_name}' deleted.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to delete cluster: {e}")
            raise

    def get_access_config(self) -> Dict[str, Any]:
        return {
            "type": "k8s",
            "kubeconfig": self.kubeconfig_path,
            "cluster_name": self.cluster_name
        }




