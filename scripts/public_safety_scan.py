"""Fail a public build on common secret, identity, or opaque-artifact hazards."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 1_000_000
DENIED_SUFFIXES = {
    ".7z",
    ".csv",
    ".db",
    ".feather",
    ".h5",
    ".joblib",
    ".key",
    ".npy",
    ".npz",
    ".onnx",
    ".parquet",
    ".pem",
    ".pickle",
    ".pkl",
    ".pt",
    ".pth",
    ".rar",
    ".sqlite",
    ".sqlite3",
    ".tgz",
    ".zip",
}

# Patterns are assembled in pieces so the scanner source does not contain a
# realistic literal secret candidate.
PATTERNS = {
    "AWS_ACCESS_KEY_SHAPE": re.compile(r"(?:AK" + r"IA|AS" + r"IA)[A-Z0-9]{16}"),
    "PRIVATE_KEY_BLOCK": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?" + r"PRIVATE KEY"),
    "GITHUB_PAT_SHAPE": re.compile(r"gh" + r"[pousr]_[A-Za-z0-9]{20,}"),
    "LITERAL_BEARER": re.compile(
        r"(?i)authorization\s*[:=]\s*[\"']?bear" + r"er\s+[A-Za-z0-9._~+/=-]{12,}"
    ),
    "JWT_SHAPE": re.compile(
        r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
    ),
    "AWS_ACCOUNT_ID": re.compile(r"(?<!\d)\d{12}(?!\d)"),
    "AWS_ARN": re.compile(r"arn:" + r"aws(?:-[a-z]+)?:[a-z0-9-]+:"),
    "EC2_INSTANCE_ID": re.compile(r"(?<![A-Za-z0-9])i-[0-9a-f]{8,17}(?![A-Za-z0-9])"),
    "WALLET_ADDRESS": re.compile(r"(?<![A-Fa-f0-9])0x[A-Fa-f0-9]{40}(?![A-Fa-f0-9])"),
    "PRIVATE_MACHINE_PATH": re.compile(r"/(?:Users|Volumes)/[A-Za-z0-9._ -]+/"),
}


def tracked_candidate_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
    )


def main() -> int:
    failures: list[str] = []

    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            failures.append(f"SYMLINK {path.relative_to(ROOT)}")

    for path in tracked_candidate_files():
        relative = path.relative_to(ROOT)
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            failures.append(f"OVERSIZE {relative} ({size} bytes)")
        if path.suffix.lower() in DENIED_SUFFIXES or path.name.endswith((".tar.gz", ".tar.xz")):
            failures.append(f"DENIED_ARTIFACT {relative}")

        data = path.read_bytes()
        if b"\x00" in data:
            failures.append(f"BINARY {relative}")
            continue
        text = data.decode("utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{label} {relative}:{line}")

    if failures:
        print("Public safety scan failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Public safety scan passed: no blocked secrets, identities, symlinks, or artifacts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
