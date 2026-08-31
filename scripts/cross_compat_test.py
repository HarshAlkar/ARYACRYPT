#!/usr/bin/env python3
"""Cross-language compatibility: Python <-> Node .arya roundtrips."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "docs" / "spec" / "test-vectors" / "vectors.json"


def main() -> int:
    from aryacrypt import AryaCrypt

    doc = json.loads(VECTORS.read_text(encoding="utf-8"))
    crypto = AryaCrypt()
    node = ROOT / "node-sdk"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Python encrypt -> Node decrypt
        for v in doc["vectors"]:
            if v.get("legacy"):
                continue
            salt = bytes.fromhex(v["salt_hex"])
            nonce = bytes.fromhex(v["nonce_hex"])
            plaintext = bytes.fromhex(v["plaintext_hex"])
            blob = crypto.encrypt(
                plaintext, v["password"], salt=salt, nonce=nonce, timestamp=v["timestamp"]
            )
            blob_path = tmp_path / f"{v['id']}.arya"
            blob_path.write_bytes(blob)
            out_path = tmp_path / f"{v['id']}.out"
            script = f"""
import {{ AryaCrypt }} from './dist/index.js';
import {{ readFileSync, writeFileSync }} from 'node:fs';
const crypto = new AryaCrypt();
const blob = readFileSync({json.dumps(str(blob_path))});
const plain = await crypto.decrypt(blob, {json.dumps(v['password'])});
writeFileSync({json.dumps(str(out_path))}, Buffer.from(plain));
"""
            r = subprocess.run(
                ["node", "--input-type=module", "-e", script],
                cwd=node,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                print(r.stderr)
                print(f"FAIL Node decrypt for {v['id']}")
                return 1
            if out_path.read_bytes() != plaintext:
                print(f"FAIL plaintext mismatch Node decrypt {v['id']}")
                return 1
            print(f"OK python->node {v['id']}")

        # Node encrypt -> Python decrypt (fixed salt/nonce via options)
        for v in doc["vectors"]:
            if v.get("legacy"):
                continue
            blob_path = tmp_path / f"node_{v['id']}.arya"
            script = f"""
import {{ AryaCrypt }} from './dist/index.js';
import {{ writeFileSync }} from 'node:fs';
const crypto = new AryaCrypt();
const plaintext = Buffer.from({json.dumps(v['plaintext_hex'])}, 'hex');
const salt = Buffer.from({json.dumps(v['salt_hex'])}, 'hex');
const nonce = Buffer.from({json.dumps(v['nonce_hex'])}, 'hex');
const blob = await crypto.encrypt(plaintext, {json.dumps(v['password'])}, {{
  salt, nonce, timestamp: {v['timestamp']}
}});
writeFileSync({json.dumps(str(blob_path))}, Buffer.from(blob));
"""
            r = subprocess.run(
                ["node", "--input-type=module", "-e", script],
                cwd=node,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                print(r.stderr)
                print(f"FAIL Node encrypt for {v['id']}")
                return 1
            blob = blob_path.read_bytes()
            # Bit-exact vs golden
            if blob.hex() != v["arya_blob_hex"]:
                print(f"FAIL node blob != golden {v['id']}")
                return 1
            plain = crypto.decrypt(blob, v["password"])
            if plain != bytes.fromhex(v["plaintext_hex"]):
                print(f"FAIL python decrypt of node blob {v['id']}")
                return 1
            print(f"OK node->python {v['id']}")

    print("All cross-language checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
