
import argparse
import random

import pytest


class RandomOrder:
    def __init__(self, seed):
        self.seed = seed

    @pytest.hookimpl
    def pytest_collection_modifyitems(self, items):
        random.Random(self.seed).shuffle(items)
        print(f"\nRandom test order seed: {self.seed}")
        print("Execution order:")
        for item in items:
            print(f"  {item.nodeid}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=429)
    args = parser.parse_args()

    pytest.main([
        "tests/",
        "-v",
    ], plugins=[RandomOrder(args.seed)])
