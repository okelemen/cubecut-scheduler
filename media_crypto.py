"""Encrypt approved media before placing it in the public scheduler repository."""

import argparse
import base64
import hashlib
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


MAGIC = b"CCUT1"


def key():
    value = base64.b64decode(os.environ["CUBECUT_MEDIA_KEY"], validate=True)
    if len(value) != 32:
        raise RuntimeError("CUBECUT_MEDIA_KEY must contain a 256-bit key")
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("encrypt", "decrypt"))
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--sha256", help="Expected plaintext SHA-256 for decryption")
    args = parser.parse_args()
    payload = args.source.read_bytes()
    cipher = AESGCM(key())
    if args.operation == "encrypt":
        nonce = os.urandom(12)
        output = MAGIC + nonce + cipher.encrypt(nonce, payload, None)
    else:
        if not payload.startswith(MAGIC) or len(payload) < len(MAGIC) + 12 + 16:
            raise RuntimeError("Invalid encrypted media")
        nonce = payload[len(MAGIC):len(MAGIC) + 12]
        output = cipher.decrypt(nonce, payload[len(MAGIC) + 12:], None)
        if args.sha256 and hashlib.sha256(output).hexdigest() != args.sha256:
            raise RuntimeError("Decrypted video differs from approved SHA-256")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    print(f"{args.operation} complete: {args.output.name}, {len(output)} bytes")


if __name__ == "__main__":
    main()
