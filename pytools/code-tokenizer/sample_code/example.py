import os

# A simple function to demonstrate
def greet(name: str) -> str:
    """Greets the user by name."""
    # Check if the name is provided
    if not name:
        return "Hello there!"
    message = f"Hello, {name}!"
    print(message) # Print the message
    return message

# Example usage
if __name__ == "__main__":
    user_name = os.getenv("USER", "World") # Default to World
    greet(user_name)
    # Calculate something simple
    a = 10
    b = 20
    print(f"{a} + {b} = {a+b}") # Basic arithmetic
