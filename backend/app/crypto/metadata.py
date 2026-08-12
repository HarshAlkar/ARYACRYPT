import json
import struct
import base64
from typing import Dict, Any, Tuple
from datetime import datetime, timezone


class MetadataError(Exception):
    """Raised when metadata parsing, validation, or serialization fails."""
    pass


class EncryptedFileMetadata:
    """
    Provides a dynamic serialization and deserialization architecture for 
    the `.arya` encrypted file format.
    
    Instead of a rigid fixed-byte header, this uses a robust, extensible 
    JSON-based header prefixed with a binary length indicator.
    
    Binary Format Structure:
    [ Magic Bytes (4 bytes: "ARYA") ]
    [ Header Length (4 bytes: Big-Endian Unsigned Integer) ]
    [ JSON Encoded Metadata String (Variable Length) ]
    [ Ciphertext Stream (Variable Length) ]
    """
    
    MAGIC_BYTES = b"ARYA"
    FRAMEWORK_VERSION = "1.1.0"
    ALGORITHM = "AryaCrypt-Aryabhata-PBKDF2-AES256GCM"

    @staticmethod
    def build(salt: bytes, nonce: bytes, auth_tag: bytes, version: int = 1) -> Dict[str, Any]:
        """
        Constructs the standardized metadata dictionary containing all 
        cryptographic and auditing parameters.
        """
        return {
            "version": version,
            "framework_version": EncryptedFileMetadata.FRAMEWORK_VERSION,
            "algorithm": EncryptedFileMetadata.ALGORITHM,
            "salt": base64.b64encode(salt).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "auth_tag": base64.b64encode(auth_tag).decode('utf-8'),
            "timestamp": int(datetime.now(timezone.utc).timestamp())
        }

    @staticmethod
    def serialize_header(metadata: Dict[str, Any]) -> bytes:
        """
        Serializes the structured metadata dictionary into the final binary 
        header format ready to be prepended to the ciphertext.
        
        Args:
            metadata: The complete metadata dictionary.
            
        Returns:
            bytes: The strict binary header payload.
        """
        try:
            # Compact JSON representation to save space
            json_bytes = json.dumps(metadata, separators=(',', ':')).encode('utf-8')
        except Exception as e:
            raise MetadataError(f"Failed to encode metadata to JSON: {e}")
            
        header_length = len(json_bytes)
        
        # struct.pack('>I') creates a 4-byte big-endian unsigned integer
        length_prefix = struct.pack('>I', header_length)
        
        return EncryptedFileMetadata.MAGIC_BYTES + length_prefix + json_bytes

    @staticmethod
    def deserialize_from_stream(in_stream) -> Tuple[Dict[str, Any], int]:
        """
        Reads directly from an open binary stream to parse the Magic Bytes, 
        calculate the Header Length, and safely extract the JSON metadata.
        
        The stream pointer is automatically advanced to the exact start of the Ciphertext.
        
        Args:
            in_stream (BinaryIO): The open file stream.
            
        Returns:
            Tuple[Dict[str, Any], int]: The parsed metadata dictionary and the 
                                        total number of header bytes consumed.
                                        
        Raises:
            MetadataError: If the file is corrupted, not an ARYA file, or JSON is invalid.
        """
        # 1. Validate Magic Bytes
        magic = in_stream.read(4)
        if magic != EncryptedFileMetadata.MAGIC_BYTES:
            raise MetadataError("Invalid file format. Magic bytes 'ARYA' not found.")
            
        # 2. Extract Header Length
        length_bytes = in_stream.read(4)
        if len(length_bytes) < 4:
            raise MetadataError("Corrupted file header. Missing 4-byte length indicator.")
            
        header_length = struct.unpack('>I', length_bytes)[0]
        
        # 3. Prevent Memory Exhaustion Attacks (Limit header to an arbitrary safe max, e.g. 10KB)
        if header_length > 10240:
            raise MetadataError(f"Unsafely massive header detected ({header_length} bytes). File may be corrupted.")
            
        # 4. Extract and Parse JSON Metadata
        json_bytes = in_stream.read(header_length)
        if len(json_bytes) < header_length:
            raise MetadataError("Unexpected end of file while reading JSON header.")
            
        try:
            metadata = json.loads(json_bytes.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise MetadataError(f"Failed to parse metadata JSON payload: {e}")
            
        total_header_bytes = 4 + 4 + header_length
        return metadata, total_header_bytes
