import base64
from typing import BinaryIO, Dict

from app.framework.aryabhata.preprocess import AryabhataPreprocessor
from app.crypto.key_manager import KeyManager
from app.crypto.aes import AESManager
from app.crypto.salt import SaltManager
from app.crypto.nonce import NonceManager


class EncryptionService:
    """
    High-level orchestrator for the AryaCrypt encryption workflow.
    
    Pipeline:
      Password → Aryabhata Base-100 Roman-Sanskrit diffusion
              → byte stream → PBKDF2-HMAC-SHA256 → AES-256-GCM
    """
    
    def __init__(self):
        self.preprocessor = AryabhataPreprocessor()

    def encrypt_file(self, password: str, in_stream: BinaryIO, out_stream: BinaryIO) -> Dict[str, str]:
        # Step 1–2: Aryabhata preprocessing
        pre = self.preprocessor.transform(password, log=False)
        
        # Step 3: Salt & Nonce
        salt = SaltManager.generate()
        nonce = NonceManager.generate()
        
        # Step 4: PBKDF2 key derivation from Aryabhata stream
        key = KeyManager.derive_key(aryacrypt_stream=pre.stream_bytes, salt=salt)
        
        # Step 5: AES-256-GCM stream encrypt
        auth_tag = AESManager.encrypt_stream(
            key=key, 
            nonce=nonce, 
            in_stream=in_stream, 
            out_stream=out_stream
        )
        
        return {
            "salt": SaltManager.encode_base64(salt),
            "nonce": NonceManager.encode_base64(nonce),
            "auth_tag": base64.b64encode(auth_tag).decode('utf-8'),
            "algorithm": AryabhataPreprocessor.ALGORITHM_ID,
        }
