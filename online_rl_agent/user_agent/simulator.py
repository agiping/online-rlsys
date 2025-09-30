def get_user_task() -> str:
    """
    Returns a hardcoded user problem for the MVP.
    """
    return "My service is down, please investigate and find the root cause."

def get_reward_from_user(final_answer: str) -> int:
    """
    Shows the agent's final answer to the real user and asks for a reward.

    Args:
        final_answer: The solution proposed by the agent.

    Returns:
        An integer reward (1 for success, 0 for failure).
    """
    print("\n--- Agent's Final Proposed Solution ---")
    print(final_answer)
    print("-----------------------------------------")
    
    while True:
        try:
            reward = int(input("Was the problem solved? Enter 1 for YES, 0 for NO: "))
            if reward in [0, 1]:
                return reward
            else:
                print("Invalid input. Please enter 1 or 0.")
        except ValueError:
            print("Invalid input. Please enter a number (1 or 0).")

if __name__ == '__main__':
    # Example of how these functions would be used
    task = get_user_task()
    print(f"User Task: {task}")
    
    # Simulate an agent's answer
    agent_solution = "The root cause is that pod 'test-pod-123' is in a CrashLoopBackOff state due to a database connection error."
    user_reward = get_reward_from_user(agent_solution)
    
    print(f"\nUser provided reward: {user_reward}")
