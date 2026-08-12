# AryaCrypt Algorithm Design

## 1. Algorithm Pipeline Explanation
The AryaCrypt algorithm introduces a custom mathematical preprocessing layer while strictly preserving the integrity of standard cryptographic primitives (AES-256, PBKDF2, and SHA256). The pipeline functions as follows:

1. **Input:** The algorithm receives a raw input, typically a user password or a high-entropy seed.
2. **Transformation:** The raw input is transformed into a standardized numeric format. For instance, a string is converted into its underlying byte/integer representation to allow for mathematically sound arithmetic operations.
3. **Roman/Positional Mapping:** The large integer is fragmented based on place-value systems (units, tens, hundreds). In the Aryabhata system, numbers are evaluated in base-100, distinguishing between odd places (Varga) and even places (Avarga).
4. **Aryabhata Encoding (Custom Preprocessing):** The mapped positional values are translated into phonetic components based on historical mathematical rules:
   - *Varga* values (1-25) map to specific consonants (k to m).
   - *Avarga* values (30-100) map to other consonants (y to h).
   - Powers of 100 map to vowels (a, i, u, etc.).
5. **Numeric Stream (Encoded Output):** The phonetic components are concatenated to form a highly obscure, deterministic "Aryabhata String". This acts as a high-complexity pre-image.
6. **Key Derivation (Unmodified):** The Aryabhata String is passed as the secret directly into unmodified PBKDF2 (using SHA256 as the underlying hashing algorithm) along with a cryptographic salt. The output is a standard, secure 256-bit (32-byte) key.
7. **AES (Unmodified):** The derived 256-bit key is used in an unmodified AES-256 algorithm (e.g., AES-GCM) for secure file encryption.

---

## 2. Pseudo Code

```text
// 1. Constants based on Aryabhata System
VARGA_CONSONANTS = ['k', 'kh', 'g', 'gh', 'ng', 'c', 'ch', 'j', 'jh', 'ny', 't', 'th', 'd', 'dh', 'n', 't', 'th', 'd', 'dh', 'n', 'p', 'ph', 'b', 'bh', 'm']
AVARGA_CONSONANTS = ['y', 'r', 'l', 'v', 'sh', 'ss', 's', 'h']
VOWEL_MULTIPLIERS = ['a', 'i', 'u', 'r', 'l', 'e', 'o', 'ai', 'au'] // Representing 100^0, 100^1, 100^2, etc.

// 2. Custom Preprocessing: Aryabhata Encoding Engine (AEE)
FUNCTION EncodeAryabhata(numeric_value):
    encoded_string = ""
    power = 0
    
    WHILE numeric_value > 0:
        remainder = numeric_value MOD 100
        numeric_value = numeric_value DIV 100
        
        vowel = VOWEL_MULTIPLIERS[power MOD length(VOWEL_MULTIPLIERS)]
        
        IF remainder > 0 AND remainder <= 25:
            // Varga Processing
            consonant = VARGA_CONSONANTS[remainder - 1]
            encoded_string = consonant + vowel + encoded_string
        ELSE IF remainder > 25:
            // Avarga Processing (Simplified logical mapping)
            tens = (remainder DIV 10) * 10
            units = remainder MOD 10
            
            IF tens >= 30:
                avarga_index = (tens - 30) DIV 10
                consonant = AVARGA_CONSONANTS[avarga_index]
                encoded_string = consonant + vowel + encoded_string
            
            IF units > 0:
                consonant_unit = VARGA_CONSONANTS[units - 1]
                encoded_string = consonant_unit + vowel + encoded_string
        
        power = power + 1
        
    RETURN encoded_string

// 3. Main Workflow
FUNCTION AryaCryptMain(password, file_data):
    // Step 1 & 2: Input & Transformation
    numeric_seed = ConvertToInteger(password)
    
    // Step 3 & 4: Roman Mapping & Aryabhata Encoding
    aryabhata_stream = EncodeAryabhata(numeric_seed)
    
    // Step 5 & 6: Key Derivation (Standard PBKDF2-HMAC-SHA256)
    salt = GenerateSecureRandomSalt(16)
    iterations = 600000
    key_length = 32 // 256 bits
    
    aes_key = PBKDF2_SHA256(secret=aryabhata_stream, salt=salt, iterations=iterations, dkLen=key_length)
    
    // Step 7: AES Encryption (Standard AES-256-GCM)
    iv = GenerateSecureRandomIV(12)
    ciphertext, auth_tag = AES_GCM_256_Encrypt(key=aes_key, iv=iv, plaintext=file_data)
    
    RETURN (salt, iv, auth_tag, ciphertext)
```

---

## 3. Flowchart
```mermaid
flowchart TD
    A[Input: Password / Seed] --> B[Transformation: String to Integer]
    B --> C[Roman Mapping: Base-100 Grouping]
    C --> D[Aryabhata Encoding Engine]
    D --> E[Numeric Stream: Aryabhata String]
    E --> F[PBKDF2-HMAC-SHA256]
    S[Secure Random Salt] --> F
    F --> G[Derived 256-bit AES Key]
    G --> H[AES-256 Engine]
    IV[Secure Random IV] --> H
    P[Plaintext File] --> H
    H --> I[Ciphertext + Metadata]
```

---

## 4. Architecture Diagram
```mermaid
flowchart LR
    subgraph Custom Preprocessing Layer
        A[Input Module] --> B[Numeric Transformer]
        B --> C[Aryabhata Encoding Engine]
    end

    subgraph Standard Cryptographic Layer
        C -->|Aryabhata String| D[PBKDF2-HMAC-SHA256]
        D -->|256-bit Key| E[AES-256-GCM]
    end

    subgraph I/O Layer
        E --> F[Secure File Storage]
    end
```

---

## 5. State Diagram
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Transforming: Receive Input
    Transforming --> Mapping: Extract Integer Value
    Mapping --> VargaAvargaSplitting: Base-100 Division
    
    state VargaAvargaSplitting {
        [*] --> CheckRemainder
        CheckRemainder --> ProcessVarga: Remainder <= 25
        CheckRemainder --> ProcessAvarga: Remainder > 25
        ProcessVarga --> AppendVowel
        ProcessAvarga --> AppendVowel
        AppendVowel --> CheckRemainder: More digits exist
    }
    
    VargaAvargaSplitting --> StreamAssembled: All digits encoded
    StreamAssembled --> KeyDerivation: Send to PBKDF2
    KeyDerivation --> Encryption: 256-bit AES Key Ready
    Encryption --> [*]: Ciphertext Generated
```

---

## 6. Sequence Diagram
```mermaid
sequenceDiagram
    actor User
    participant App as AryaCrypt App
    participant AEE as Aryabhata Engine (Custom)
    participant KDF as PBKDF2-SHA256 (Standard)
    participant AES as AES-256 (Standard)
    
    User->>App: Provides Password & File
    App->>AEE: Send Password (Input)
    AEE->>AEE: Transform to Integer
    AEE->>AEE: Apply Roman Mapping (Base-100)
    AEE->>AEE: Encode to Aryabhata String
    AEE-->>App: Return Numeric Stream (String)
    
    App->>KDF: PBKDF2(Stream, Salt, 600k Iterations)
    KDF-->>App: Return 256-bit AES Key
    
    App->>AES: AES_Encrypt(File, Key, IV)
    AES-->>App: Return Ciphertext + AuthTag
    App-->>User: File Encrypted Successfully
```
