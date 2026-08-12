# Literature Review and Research Gap Analysis

## 1. Existing Technologies & Methodologies

### 1.1 Aryabhata Number System
*   **Overview:** Developed in the 5th century by Indian mathematician Aryabhata, this alphasyllabic system maps numbers to consonants and powers of 100 to vowels.
*   **Strengths:** Extremely high data density; deterministic but obscure mapping; capable of representing very large integers compactly.
*   **Weaknesses:** Not designed for binary computation; highly complex to parse programmatically; historically used for astronomy, not cryptography.

### 1.2 Ancient Mathematics in Cryptography
*   **Overview:** Previous research has predominantly focused on Vedic Mathematics (e.g., *Urdhva Tiryakbhyam* sutra) to optimize hardware multipliers for RSA and Elliptic Curve Cryptography (ECC).
*   **Strengths:** Reduces hardware logic gates and computational latency in asymmetric cryptography.
*   **Weaknesses:** Almost exclusively focused on mathematical *optimization* (speed), ignoring *entropy* and *key generation* complexity.

### 1.3 Key Derivation (PBKDF2, SHA256)
*   **Overview:** PBKDF2 uses a pseudorandom function (like HMAC-SHA256) to derive keys from a password, utilizing a salt and many iterations.
*   **Strengths:** Cryptographically proven; standard compliance (NIST); slows down brute-force attacks via iteration count.
*   **Weaknesses:** Vulnerable to ASIC/GPU farms optimized for SHA256; susceptible to dictionary attacks if the initial input lacks entropy.

### 1.4 AES-256
*   **Overview:** The gold standard for symmetric block ciphers.
*   **Strengths:** Mathematically secure against classical and quantum (via Grover's algorithm mitigation) attacks if the key is truly random.
*   **Weaknesses:** Entirely dependent on the secrecy and entropy of the key. A weak key compromises the entire algorithm.

## 2. Comparative Analysis
| Domain | Focus | Strengths | Weaknesses |
| :--- | :--- | :--- | :--- |
| **Traditional PBKDF2** | Standardized Hashing | Cryptographically proven | ASIC-optimized cracking exists |
| **Vedic Math Crypto** | Hardware Optimization | Faster RSA/ECC multiplication | Doesn't improve key entropy |
| **AryaCrypt** | Pre-hash Diffusion | Disrupts rainbow tables/ASICs | Slight computational overhead |

## 3. Identified Research Gaps
1. **Lack of Pre-Hash Diffusion:** Current password-based KDFs directly hash numeric or string inputs. There is no intermediate algorithmic diffusion layer that transforms the input structurally before hashing.
2. **Underutilization of Historical Linguistics:** While historical math is used for optimization, historical *linguistic mapping* (like alphasyllabaries) has never been used for deterministic key stretching or entropy obfuscation.
3. **Hardware Cracking Optimization:** Because SHA256 and PBKDF2 are standards, attackers build specialized hardware to crack them. An unconventional pre-processing step thwarts generic hardware cracking pipelines.

## 4. The Gap AryaCrypt Solves
**AryaCrypt bridges the gap between historical linguistics and modern cryptographic diffusion.**
By transforming a numerical seed into an Aryabhata alphasyllabic string *before* applying PBKDF2, AryaCrypt forces attackers to compute an intermediate, non-standard linguistic translation step. This effectively neutralizes pre-computed rainbow tables and heavily degrades the efficiency of ASIC/GPU-based password cracking farms, adding a novel layer of software-based algorithmic complexity to standard cryptographic pipelines.
