import io
from pathlib import Path

from aryacrypt import AryaCrypt
from aryacrypt import aes_gcm, format as arya_format, kdf, preprocess
from aryacrypt.constants import ALGORITHM_ID, NONCE_LENGTH_BYTES, SALT_LENGTH_BYTES
import os


def test_aryabhata_pbkdf2_aes_roundtrip(tmp_path: Path):
    password = "testpass99"
    plaintext = b"AryaCrypt vault payload " * 200

    salt = os.urandom(SALT_LENGTH_BYTES)
    nonce = os.urandom(NONCE_LENGTH_BYTES)
    _, stream, _, _ = preprocess.transform_password(password)
    key = kdf.derive_key(stream, salt)

    cipher_path = tmp_path / "cipher.bin"
    with open(cipher_path, "wb") as out:
        tag = aes_gcm.encrypt_stream(key, nonce, io.BytesIO(plaintext), out)

    meta = arya_format.build_metadata(salt, nonce, tag)
    header = arya_format.serialize_header(meta)
    arya_path = tmp_path / "sample.arya"
    with open(arya_path, "wb") as f:
        f.write(header)
        f.write(cipher_path.read_bytes())

    with open(arya_path, "rb") as stream_in:
        parsed, _ = arya_format.deserialize_from_stream(stream_in)
        assert ALGORITHM_ID in parsed["algorithm"] or parsed["algorithm"]
        assert preprocess.uses_aryabhata(parsed["algorithm"])

        import base64

        salt2 = base64.b64decode(parsed["salt"])
        nonce2 = base64.b64decode(parsed["nonce"])
        tag2 = base64.b64decode(parsed["auth_tag"])
        _, stream2, _, _ = preprocess.transform_password(password)
        key2 = kdf.derive_key(stream2, salt2)
        out_path = tmp_path / "plain.bin"
        with open(out_path, "wb") as plain_out:
            aes_gcm.decrypt_stream(key2, nonce2, tag2, stream_in, plain_out)

    assert out_path.read_bytes() == plaintext


def test_sdk_high_level_roundtrip():
    crypto = AryaCrypt()
    data = b"sdk high level"
    blob = crypto.encrypt(data, "password1")
    assert crypto.decrypt(blob, "password1") == data


def test_encrypt_decrypt_api_roundtrip(client, auth_headers):
    headers, _ = auth_headers
    content = b"hello vault world " * 50
    files = {"file": ("note.txt", io.BytesIO(content), "text/plain")}
    data = {"password": "vaultpass1"}

    enc = client.post("/api/v1/files/encrypt", headers=headers, files=files, data=data)
    assert enc.status_code == 200, enc.text
    meta = enc.json()
    assert meta["original_name"] == "note.txt"
    assert meta["file_size_bytes"] > 0
    file_id = meta["id"]

    history = client.get("/api/v1/files/history", headers=headers)
    assert history.status_code == 200
    assert any(f["id"] == file_id for f in history.json())

    stats = client.get("/api/v1/files/stats", headers=headers)
    assert stats.status_code == 200
    body = stats.json()
    assert body["total_files"] >= 1
    assert body["total_encrypted"] >= 1

    bad = client.post(
        f"/api/v1/files/{file_id}/decrypt",
        headers=headers,
        data={"password": "wrongpass1"},
    )
    assert bad.status_code == 401

    stats2 = client.get("/api/v1/files/stats", headers=headers)
    assert stats2.json()["security_alerts"] >= 1

    good = client.post(
        f"/api/v1/files/{file_id}/decrypt",
        headers=headers,
        data={"password": "vaultpass1"},
    )
    assert good.status_code == 200
    assert good.content == content

    stats3 = client.get("/api/v1/files/stats", headers=headers)
    assert stats3.json()["total_decrypted"] >= 1

    deleted = client.delete(f"/api/v1/files/{file_id}", headers=headers)
    assert deleted.status_code == 204
