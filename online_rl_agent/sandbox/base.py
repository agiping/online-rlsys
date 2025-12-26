from abc import ABC, abstractmethod
from typing import Any, Dict

class Sandbox(ABC):
    """
    Abstract base class for a sandbox environment.
    """
    
    @abstractmethod
    def start(self) -> None:
        """Starts the sandbox environment."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stops and tears down the sandbox environment."""
        pass

    @abstractmethod
    def get_access_config(self) -> Dict[str, Any]:
        """
        Returns configuration needed to access the sandbox 
        (e.g., kubeconfig path, connection details).
        """
        pass




