from abc import ABC, abstractmethod

class BaseEnvironment(ABC):
    """
    An abstract base class for defining an environment for the RL agent.
    
    This class defines the standard lifecycle methods that any environment
    must implement to be compatible with the main RL loop.
    """

    @abstractmethod
    def setup(self):
        """
        Sets up the environment for a new episode.
        This could involve injecting a fault, resetting a simulation, etc.
        """
        pass

    @abstractmethod
    def get_task(self) -> str:
        """
        Gets the task or problem description for the current episode.
        
        Returns:
            A string describing the task for the agent.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Cleans up the environment after an episode is finished.
        This could involve deleting a fault, restoring state, etc.
        """
        pass
