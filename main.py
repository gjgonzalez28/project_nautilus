import sys
from logic.manager import NautilusManager
from logic.discovery_script import DiscoveryScript

def start_nautilus():
    # 1. Initialize the Brain (Manager)
    manager = NautilusManager()
    
    # 2. Initialize the Gatekeeper (Discovery Script)
    discovery = DiscoveryScript(manager)

    print("\n" + "="*40)
    print("   PROJECT NAUTILUS: START-TO-FINISH")
    print("="*40)
    print("System: Online. Type 'exit' to shut down.")

    while True:
        # This creates the interactive prompt in your terminal
        user_input = input("\nYOU: ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("\nShutting down system...")
            break

        # Check if the user still needs to declare machine/skill or confirm playfield access
        if discovery.awaiting_discovery or manager.session.awaiting_playfield_confirmation:
            response = discovery.process_initial_response(user_input)
            print(f"\nNAUTILUS: {response}")
        else:
            # Once session is locked, use the standard diagnostic logic
            response = manager.ask(user_input)
            print(f"\nNAUTILUS: {response}")

if __name__ == "__main__":
    start_nautilus()
