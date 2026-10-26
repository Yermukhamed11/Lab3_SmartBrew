"""Build a Canvas submission ZIP from public project artifacts, excluding runtime data."""

import argparse
from pathlib import Path
import zipfile


def package(destination: Path) -> int:
    """Create a submission ZIP from the public project artifact allowlist.

    Inputs: destination is a Path to a ZIP file; its parent directory must exist.
    Returns: int, number of archived files. Writes the ZIP and overwrites an
    existing destination. Excludes runtime databases, credentials and Git data.
    """
    root = Path(__file__).resolve().parent.parent
    roots = ['app.py', 'README.md', 'requirements.txt', '.python-version', '.gitignore',
             'static', 'tests', 'docs', 'scripts', '.github']
    count = 0
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in roots:
            path = root / name
            candidates = [path] if path.is_file() else sorted(path.rglob('*'))
            for candidate in candidates:
                if not candidate.is_file() or '__pycache__' in candidate.parts or candidate.suffix == '.pyc':
                    continue
                if candidate.resolve() == destination.resolve():
                    continue
                archive.write(candidate, Path('Lab3_SmartBrew') / candidate.relative_to(root))
                count += 1
    return count


def main():
    """Parse optional ZIP output path, create the archive and print its file count; return None."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[2] / 'SmartBrew_Lab3_Submission.zip')
    args = parser.parse_args()
    count = package(args.output)
    print(f'Created {args.output} ({count} files; runtime database and credentials excluded).')


if __name__ == '__main__':
    main()
