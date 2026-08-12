# AryaCrypt: Integration of Aryabhata Number System with AES-256 for Secure Key Generation and File Encryption

## 1. Problem Statement
While Advanced Encryption Standard (AES-256) provides robust, quantum-resistant symmetric encryption, its security inherently relies on the unpredictability and entropy of the generated cryptographic keys. Conventional Pseudo-Random Number Generators (PRNGs) and standard Key Derivation Functions (KDFs) can exhibit deterministic vulnerabilities or suffer from limited structural diversity. A compromise in the key generation phase renders the underlying AES-256 encryption obsolete. There is an imperative need for an intermediate, non-linear abstraction layer in key derivation protocols to obscure seed relationships and enhance cryptographic complexity against advanced cryptanalysis and brute-force methodologies.

## 2. Why this Framework is Required
Introducing historical mathematical paradigms into modern cryptography provides a unique vector for algorithmic obfuscation. The Aryabhata numeration system is an ancient, highly structured alphasyllabic mapping mechanism that converts large numerical values into deterministic, yet highly non-linear, phonetic strings (using Sanskrit *varga* and *avarga* consonants paired with vowel multipliers). 
Integrating this system introduces an unconventional algorithmic transformation layer. This framework is required to bridge classical mathematical theories with modern cybersecurity, providing a novel methodology for key generation that resists standard dictionary attacks, mitigates predictable PRNG patterns, and acts as a complex diffusion layer prior to AES processing.

## 3. Existing Encryption Workflow
1. **Seed Generation:** A Cryptographically Secure Pseudo-Random Number Generator (CSPRNG) or user password generates an initial seed.
2. **Key Derivation:** The seed is passed through a standard hashing algorithm (e.g., PBKDF2, scrypt, or SHA-256) to stretch it into a 256-bit key.
3. **Initialization:** An Initialization Vector (IV) or Nonce is generated.
4. **Encryption:** The plaintext data is divided into blocks (usually padded) and encrypted using the 256-bit key and IV via AES (in modes like CBC, CTR, or GCM).
5. **Storage/Transmission:** The Ciphertext, IV, and any salt are stored or transmitted.

## 4. Existing Limitations
* **Algorithmic Homogeneity:** The reliance on standardized KDF pipelines means attackers can optimize hardware (ASICs/GPUs) specifically for breaking these standard mathematical transformations.
* **Seed Vulnerability:** If the initial PRNG state is compromised or weakly seeded, the resulting AES key can be reverse-engineered.
* **Lack of Intermediate Diffusion:** Standard pipelines map numerical seeds directly to binary keys without intermediate structural transformations, leaving them vulnerable to algebraic attacks if patterns are discovered in the CSPRNG.

## 5. Proposed AryaCrypt Framework
The AryaCrypt framework introduces a hybrid cryptographic architecture that overlays the Aryabhata numeration system onto a standard AES-256 pipeline. Instead of deriving the AES key directly from a PRNG seed or password, the initial numeric seed is mathematically transformed into an Aryabhata alphasyllabic string. This string, characterized by complex phonetic mappings and vowel-based exponential shifts (powers of 100), serves as a high-complexity intermediate pre-image. This pre-image is then cryptographically hashed to derive the final 256-bit AES key. The framework ensures authenticated, secure file encryption by employing AES-256-GCM (Galois/Counter Mode) utilizing this uniquely derived key.

## 6. Framework Components
The framework comprises five distinct decoupled components:
1. **Entropy Generation Module (EGM):** Responsible for collecting initial systemic entropy or user credentials.
2. **Aryabhata Encoding Engine (AEE):** The core novelty component; translates numeric data into Aryabhata phonetic representation.
3. **Cryptographic Key Derivation Function (CKDF):** Hashes the intermediate string to produce a fixed-length 256-bit symmetric key.
4. **AES-256 Encryption/Decryption Core (AEC):** The standard encryption engine utilizing AES-GCM.
5. **Secure File I/O Manager (SFIM):** Handles stream-based reading/writing of files to ensure memory safety for large datasets.

## 7. Module Responsibilities
* **EGM:** Generates a 256-bit pseudo-random integer or securely captures a user passphrase. Applies initial salting.
* **AEE:** Implements the Aryabhata algorithm. It parses the 256-bit integer, identifies *Varga* (1-25) and *Avarga* (30-100) placements, and applies vowel multipliers (powers of 100) to construct a localized string array representing the ancient numeric encoding.
* **CKDF:** Ingests the encoded string from the AEE and passes it through a memory-hard KDF (such as Argon2id) to derive the ultimate 32-byte (256-bit) AES key. This ensures the output is standard-compliant.
* **AEC:** Manages block encryption. It generates a 96-bit Nonce for AES-GCM, processes plaintext in memory-safe chunks, and appends a 128-bit authentication tag to the ciphertext to ensure data integrity.
* **SFIM:** Orchestrates file chunking (e.g., 4MB blocks). It securely prepends metadata (Salt, Nonce, Tag) to the ciphertext file header during encryption and parses it during decryption.

## 8. Data Flow
1. **Input Phase:** System provides a random 256-bit integer (S).
2. **Transformation Phase:** 
   * S $\rightarrow$ AEE $\rightarrow$ $String_{Aryabhata}$
   * $String_{Aryabhata}$ $\rightarrow$ Argon2id $\rightarrow$ $Key_{AES-256}$ (32 bytes)
3. **Encryption Phase:** 
   * Plaintext File $F_{plain}$ $\rightarrow$ SFIM $\rightarrow$ $C_1, C_2, ... C_n$ (Chunks)
   * ($C_i$, $Key_{AES-256}$, Nonce) $\rightarrow$ AEC $\rightarrow$ $Ciphertext\_Chunk_i$ + AuthTag
4. **Output Phase:** Salt + Nonce + AuthTag + $\sum Ciphertext\_Chunk_i$ $\rightarrow$ SFIM $\rightarrow$ $F_{cipher}$

## 9. Workflow
### Key Generation & Encryption
1. **Trigger:** User initiates file encryption.
2. **Seed Generation:** EGM generates a secure random seed.
3. **Encoding:** AEE translates the numeric seed into an Aryabhata string.
4. **Key Finalization:** CKDF hashes the string into a 256-bit key.
5. **I/O Processing:** SFIM opens the target file and initializes a read stream.
6. **Encryption Loop:** AEC processes the stream chunk-by-chunk using AES-GCM.
7. **Storage:** SFIM writes the encrypted chunks and metadata to the disk.
8. **Sanitization:** Key material in RAM is securely zeroed out.

### Decryption
1. **Trigger:** User initiates file decryption.
2. **Metadata Extraction:** SFIM reads Salt, Nonce, and AuthTag from the encrypted file header.
3. **Key Regeneration:** EGM $\rightarrow$ AEE $\rightarrow$ CKDF pipeline runs using the extracted salt and original user input to regenerate $Key_{AES-256}$.
4. **Decryption Loop:** AEC decrypts and authenticates file chunks using the regenerated key and extracted Nonce.
5. **Reconstruction:** SFIM writes the decrypted plaintext back to disk.

## 10. Architecture
The framework follows a **Layered Monolithic Architecture**:
* **Presentation/Interface Layer:** CLI or Web UI for user interactions and file selection.
* **Service Orchestration Layer:** Manages the lifecycle of encryption/decryption requests.
* **Cryptographic Abstraction Layer:** Contains the interfaces for AEE, CKDF, and AEC. This enforces the Dependency Inversion Principle, allowing the Aryabhata logic to be hot-swapped or upgraded without affecting AES logic.
* **Infrastructure Layer:** SFIM handles OS-level file streaming and memory buffer management.

## 11. Design Decisions
* **Use of AES-GCM:** Selected over CBC mode because GCM provides Authenticated Encryption with Associated Data (AEAD). This inherently prevents padding oracle attacks and ensures ciphertext integrity.
* **Argon2id for CKDF:** Chosen over PBKDF2/SHA-256 as it provides both memory and CPU hardness, heavily mitigating GPU-based brute-force attacks against the Aryabhata-encoded string.
* **Stream-Based File I/O:** The SFIM processes files in chunks rather than loading entire files into RAM, ensuring the framework can encrypt terabyte-sized files on resource-constrained hardware.
* **Deterministic Encoding:** The Aryabhata numeration is strictly deterministic; it acts as a complex diffusion layer rather than an entropy source. The actual entropy relies on the initial EGM seed, ensuring the framework remains mathematically provable.

## 12. Advantages
* **Algorithmic Heterogeneity:** Diverges from standard KDF pipelines, making targeted hardware attacks significantly more difficult due to the custom string manipulation required in the AEE phase.
* **Increased Pre-computation Resistance:** The non-standard translation phase prevents the use of existing rainbow tables or pre-computed hash databases.
* **High Security with Integrity:** The use of AES-GCM guarantees that any tampering with the encrypted file is immediately detected.
* **Cross-Disciplinary Innovation:** Successfully merges ancient Indian mathematics with modern cryptographic engineering, providing high educational and research value.

## 13. Limitations
* **Computational Overhead:** The string parsing, manipulation, and concatenation in the Aryabhata Encoding Engine introduces a slight latency penalty during the key generation phase compared to direct hashing.
* **No Added Theoretical Entropy:** The AEE only obfuscates the data; it does not increase the mathematical entropy of the original seed (as per Shannon's Information Theory). 
* **Implementation Complexity:** Custom string encoding requires stringent memory management in lower-level languages to prevent buffer overflow vulnerabilities.

## 14. Future Scope
* **Hardware Acceleration (FPGA):** Implementing the Aryabhata Encoding Engine logic directly on FPGAs to eliminate the computational overhead of string processing.
* **Dynamic IV Generation:** Expanding the Aryabhata system to generate continuous pseudo-random Initialization Vectors for each block in stream ciphers.
* **Post-Quantum Cryptography (PQC):** Integrating the AEE with lattice-based cryptography schemes (like CRYSTALS-Kyber) to secure the framework against future quantum computer attacks.
* **Steganographic Applications:** Utilizing the phonetically pronounceable Aryabhata strings as a covert channel for sharing symmetric keys verbally or within standard text.
