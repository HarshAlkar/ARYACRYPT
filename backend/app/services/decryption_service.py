import base64
from typing import BinaryIO, Dict

from app.framework.aryabhata.preprocess import AryabhataPreprocessor
from app.crypto.key_manager import KeyManager
from app.crypto.aes import AESManager
from app.crypto.salt import SaltManager
from app.crypto.nonce import NonceManager


class DecryptionService:
    """
    High-level orchestrator for the AryaCrypt decryption workflow.
    
    Replays the same Aryabhata → PBKDF2 path used at encryption time,
    then verifies AES-GCM Auth Tag before restoring plaintext.
    """
    
    def __init__(self):
        self.preprocessor = AryabhataPreprocessor()

    def decrypt_file(self, password: str, metadata: Dict[str, str], in_stream: BinaryIO, out_stream: BinaryIO) -> None:
        try:
            salt = SaltManager.decode_base64(metadata['salt'])
            nonce = NonceManager.decode_base64(metadata['nonce'])
            auth_tag = base64.b64decode(metadata['auth_tag'])
        except KeyError as e:
            raise ValueError(f"Missing essential cryptographic metadata field: {e}")
        except Exception as e:
            raise ValueError(f"Failed to safely decode cryptographic metadata: {e}")

        algorithm = metadata.get("algorithm", AryabhataPreprocessor.ALGORITHM_ID)
        use_aryabhata = AryabhataPreprocessor.uses_aryabhata(algorithm)

        if use_aryabhata:
            pre = self.preprocessor.transform(password, log=False)
            key_material = pre.stream_bytes
        else:
            key_material = password.encode("utf-8")

        key = KeyManager.derive_key(aryacrypt_stream=key_material, salt=salt)

        AESManager.decrypt_stream(
            key=key,
            nonce=nonce,
            tag=auth_tag,
            in_stream=in_stream,
            out_stream=out_stream
        )
