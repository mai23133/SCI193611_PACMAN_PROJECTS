"""Build submission archives containing exactly the requested named files."""

import hashlib
import json
from pathlib import Path
import tarfile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Write three archives and a checksum manifest; verify their contents."""
    groups = {
        'project0': ('bfs.py', 'astar.py'),
        'project1': ('minimax.py', 'hminimax.py'),
        'project2': ('bayesfilter.py', 'pacmanagent.py', 'report.pdf'),
    }
    for project, filenames in groups.items():
        for filename in filenames:
            if not (ROOT / project / filename).is_file():
                raise SystemExit(f'Missing {project}/{filename}')
    pages = len(PdfReader(ROOT / 'project2/report.pdf').pages)
    if not 1 <= pages <= 5:
        raise SystemExit(f'Report must contain 1 to 5 pages; found {pages}')
    output = ROOT / 'deliverables'
    output.mkdir(exist_ok=True)
    manifest = {}
    for project, filenames in groups.items():
        archive = output / f'{project}.tar.gz'
        with tarfile.open(archive, 'w:gz') as bundle:
            for filename in filenames:
                bundle.add(ROOT / project / filename, arcname=filename)
        with tarfile.open(archive) as bundle:
            if sorted(bundle.getnames()) != sorted(filenames):
                raise SystemExit(f'Unexpected files in {archive}')
            for filename in filenames:
                if (bundle.extractfile(filename).read()
                        != (ROOT / project / filename).read_bytes()):
                    raise SystemExit(f'Content mismatch: {project}/{filename}')
        manifest[archive.name] = {
            'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'files': {name: hashlib.sha256(
                (ROOT / project / name).read_bytes()).hexdigest()
                for name in filenames},
        }
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Created {len(groups)} archives in {output}')


if __name__ == '__main__':
    main()
