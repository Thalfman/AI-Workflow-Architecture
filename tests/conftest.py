import sys
from pathlib import Path

# The repo's scripts live in scripts/ (not an installable package), so make them
# importable by the test suite.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
