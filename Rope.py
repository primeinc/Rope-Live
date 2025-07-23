#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.INFO)

from rope import Coordinator
if __name__ == "__main__":
    Coordinator.run()