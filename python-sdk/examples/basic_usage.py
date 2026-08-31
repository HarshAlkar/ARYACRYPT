from aryacrypt import AryaCrypt

crypto = AryaCrypt()
blob = crypto.encrypt(b"hello from example", "example1")
assert crypto.decrypt(blob, "example1") == b"hello from example"
print("ok", len(blob), "bytes")
