import requests
import json
import logging
from typing import Dict, Any, Optional

# Assuming k8s_tools.py and prompts.py are in the same package or accessible through PYTHONPATH
from online_rl_agent.tools import k8s_tools
from online_rl_agent.agent.prompts import SYSTEM_PROMPT
from online_rl_agent.data.trajectory_store import TrajectoryStore

# Try to import config, but handle the case where it doesn't exist yet
try:
    from online_rl_agent import config
except ImportError:
    # This allows the module to be imported without a config.py file,
    # which is useful for testing or if config is handled differently.
    config = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DevOpsAgent:
    def __init__(self, api_key: str = None, model: str = "deepseek-chat", kubeconfig: Optional[str] = None):
        """
        Initializes the DevOpsAgent.

        Args:
            api_key: The DeepSeek API key. If not provided, it will try to get it from config.
            model: The name of the model to use.
            kubeconfig: Optional path to a kubeconfig file to restrict the agent's scope.
        """
        if api_key:
            self.api_key = api_key
        elif config and hasattr(config, 'DEEPSEEK_API_KEY'):
            self.api_key = config.DEEPSEEK_API_KEY
        else:
            raise ValueError("DeepSeek API key not provided or found in config.")
        
        if "YOUR_DEEPSEEK_API_KEY" in self.api_key:
            raise ValueError("Please replace 'YOUR_DEEPSEEK_API_KEY' with your actual key in config.py.")
            
        self.model = model
        self.kubeconfig = kubeconfig
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.session = requests.Session()
        
        # Define available tools and wrap them with partial if kubeconfig is provided
        from functools import partial
        
        base_tools = {
            "get_pods": k8s_tools.get_pods,
            "describe_pod": k8s_tools.describe_pod,
            "get_pod_logs": k8s_tools.get_pod_logs,
        }
        
        self.available_tools = {}
        for name, func in base_tools.items():
            if self.kubeconfig:
                self.available_tools[name] = partial(func, kubeconfig=self.kubeconfig)
            else:
                self.available_tools[name] = func
                
        self.conversation_history = []

    def _call_llm(self, messages: list) -> Dict[str, Any]:
        """
        Calls the language model API.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1, # Lower temperature for more deterministic tool use
            "max_tokens": 4096,
        }
        try:
            response = self.session.post(self.api_url, headers=self.headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API call failed: {e}")
            raise

    def run(self, user_problem: str, max_steps: int = 10, trajectory_store: Optional[TrajectoryStore] = None) -> str:
        """
        Runs the agent to solve a user's problem.
        """
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_problem}
        ]
        
        for step in range(max_steps):
            logging.info(f"--- Step {step + 1} ---")
            
            response_json = self._call_llm(self.conversation_history)
            assistant_message = response_json['choices'][0]['message']
            
            # The model should return content in a specific JSON format.
            # We need to parse it to decide the next action.
            try:
                # The response might contain markdown ```json ... ```, let's strip it.
                content = assistant_message['content']
                if content.strip().startswith("```json"):
                    content = content.strip()[7:-4]

                action_json = json.loads(content)
                thought = action_json.get("thought", "")
                tool_name = action_json.get("tool_name", "")
                tool_args = action_json.get("tool_args", {})
                
                logging.info(f"Thought: {thought}")
                logging.info(f"Action: {tool_name}({tool_args})")

                self.conversation_history.append({"role": "assistant", "content": content})

                if tool_name == "final_answer":
                    final_answer = tool_args.get("answer", "No answer provided.")
                    logging.info(f"Final Answer: {final_answer}")
                    if trajectory_store:
                        trajectory_store.add_final_answer(final_answer)
                    return final_answer

                if tool_name in self.available_tools:
                    tool_function = self.available_tools[tool_name]
                    tool_output = tool_function(**tool_args)
                    
                    if trajectory_store:
                        trajectory_store.add_step(thought, tool_name, tool_args, tool_output)
                        
                    # Add tool output to history for the next turn
                    tool_message = f"Tool {tool_name} output:\n{tool_output}"
                    logging.info(tool_message)
                    self.conversation_history.append({"role": "user", "content": tool_message})
                else:
                    error_message = f"Error: Unknown tool '{tool_name}'."
                    logging.error(error_message)
                    if trajectory_store:
                        trajectory_store.add_step(thought, tool_name, tool_args, error_message)
                    self.conversation_history.append({"role": "user", "content": error_message})

            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"Failed to parse model output: {assistant_message.get('content', '')}. Error: {e}")
                # If parsing fails, we add an error message to the conversation and let the model try to recover.
                error_message = "Error: Your response was not in the expected JSON format. Please correct your output."
                if trajectory_store:
                    trajectory_store.add_step("Error in parsing LLM output", "error", {}, error_message)
                self.conversation_history.append({"role": "user", "content": error_message})
        
        return "Agent could not reach a final answer within the step limit."

if __name__ == '__main__':
    # This is for manual testing.
    # Make sure you have a `config.py` file in `online_rl_agent/` with your DEEPSEEK_API_KEY.
    # Example:
    # DEEPSEEK_API_KEY = "sk-..."
    
    if not config or "YOUR_DEEPSEEK_API_KEY" in config.DEEPSEEK_API_KEY:
        print("Please create and configure `online_rl_agent/config.py` before running the agent.")
    else:
        agent = DevOpsAgent(model="deepseek-coder")
        problem = "List all pods in the 'default' namespace and tell me their status."
        # problem = "My service is down." # A more realistic problem
        
        try:
            solution = agent.run(problem)
            print("\n--- Agent's Final Solution ---")
            print(solution)
        except (ValueError, requests.exceptions.RequestException) as e:
            print(f"\nAn error occurred: {e}")
