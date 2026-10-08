#!/usr/bin/env python3
"""Configure Claude context paths without changing permissions or user settings."""
from pathlib import Path
import argparse
import json
import os
import tempfile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', type=Path, help='Checkout whose local settings to update')
    parser.add_argument('--context-root', type=Path, help='Explicit shared local memory root; plans always stay inside checkout')
    args = parser.parse_args()
    checkout = (args.checkout or Path(__file__).resolve().parents[1]).resolve()
    context = (args.context_root or checkout).resolve()
    if not (checkout / '.git').exists():
        parser.error('checkout must be a Git repository or worktree')
    for name in ('AGENTS.md', 'docs/memory/MEMORY.md', 'docs/plans/README.md'):
        if not (context / name).is_file():
            parser.error(f'context root missing {name}')
    path = checkout / '.claude/settings.local.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    (checkout / 'docs/plans').mkdir(parents=True, exist_ok=True)
    data.update(plansDirectory='docs/plans',
                autoMemoryDirectory=str(context / 'docs/memory'), autoMemoryEnabled=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(data, indent=2) + '\n')
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    print(f'Configured {checkout.name}: context = {context}')

if __name__ == '__main__':
    main()
