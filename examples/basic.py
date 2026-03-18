"""Basic usage example for swara."""
from src.core import Swara

def main():
    instance = Swara(config={"verbose": True})

    print("=== swara Example ===\n")

    # Run primary operation
    result = instance.compose(input="example data", mode="demo")
    print(f"Result: {result}")

    # Run multiple operations
    ops = ["compose", "synthesize", "render]
    for op in ops:
        r = getattr(instance, op)(source="example")
        print(f"  {op}: {"✓" if r.get("ok") else "✗"}")

    # Check stats
    print(f"\nStats: {instance.get_stats()}")

if __name__ == "__main__":
    main()
