import argparse
import os
from pathlib import Path

CACHE_DIRS = [
    '~/Library/Caches',
    '~/Library/Logs',
    '~/.npm/_cacache',
    '~/.cache',
]
SAFE_SUFFIXES = {'.log', '.tmp', '.cache'}
REVIEW_SUFFIXES = {'.db', '.sqlite', '.json'}


def human(n):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f'{n:.1f}{unit}'
        n /= 1024
    return f'{n:.1f}TB'


def scan(limit=10):
    items = []
    for raw in CACHE_DIRS:
        root = Path(os.path.expanduser(raw))
        if not root.exists():
            continue
        for path in root.rglob('*'):
            try:
                if path.is_file():
                    size = path.stat().st_size
                    risk = 'safe' if path.suffix in SAFE_SUFFIXES else 'review'
                    items.append((size, risk, path))
            except OSError:
                continue
    return sorted(items, reverse=True)[:limit]


def classify(items):
    out = []
    for size, risk, path in items:
        if risk == 'safe' and size > 1024:
            action = 'delete'
        elif path.name.startswith('com.apple') or path.suffix in REVIEW_SUFFIXES:
            action = 'keep'
        else:
            action = 'ask'
        out.append((size, action, path))
    return out


def main():
    parser = argparse.ArgumentParser(description='Purrge demo: AI-assisted disk cleanup')
    parser.add_argument('--clean', action='store_true', help='actually delete confirmed items')
    args = parser.parse_args()
    candidates = classify(scan())
    print('Purrge found:')
    for i, (size, action, path) in enumerate(candidates, 1):
        print(f'{i}. [{action}] {human(size):>8} {path}')
    if not args.clean:
        print('Dry-run only. Re-run with --clean to delete safe items.')
        return
    for size, action, path in candidates:
        if action == 'delete':
            ans = input(f'Delete {path} ({human(size)})? [y/N] ')
            if ans.lower() == 'y':
                try:
                    path.unlink()
                    print(f'Deleted {path}')
                except OSError as exc:
                    print(f'Skip {path}: {exc}')


if __name__ == '__main__':
    main()