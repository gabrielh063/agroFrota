"""Run the full suite on an exclusively owned disposable MariaDB instance."""
import re
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def main():
    command = [sys.executable, str(BACKEND / 'tools/ambiente_descartavel.py')]
    started = subprocess.run(command + ['start'], cwd=BACKEND, text=True,
                             stdout=subprocess.PIPE, check=True)
    match = re.search(r'^Ambiente descartável: (.+)$', started.stdout, re.MULTILINE)
    if not match:
        raise RuntimeError('Bootstrap não retornou a identidade do ambiente.')
    directory = match.group(1)
    try:
        return subprocess.call(command + ['test', directory, 'tests'], cwd=BACKEND)
    finally:
        subprocess.run(command + ['stop', directory], cwd=BACKEND, check=True)


if __name__ == '__main__':
    raise SystemExit(main())
