import os
import shutil
from pathlib import Path


def main():
    source = Path(__file__).resolve().with_name("entry.png")
    image = source.read_bytes()
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")).resolve()
    if output in source.parents:
        raise ValueError("The output directory must not contain the source repository")
    output.mkdir(parents=True, exist_ok=True)
    for child in sorted(output.iterdir(), key=lambda item: item.name):
        if child.is_symlink() or not child.is_dir():
            child.unlink()
        else:
            shutil.rmtree(child)
    (output / "entry.png").write_bytes(image)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
