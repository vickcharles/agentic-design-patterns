import sys
from unittest.mock import MagicMock

# Mock external dependencies before any feature module is imported
sys.modules["aisuite"] = MagicMock()
sys.modules["dotenv"] = MagicMock()
