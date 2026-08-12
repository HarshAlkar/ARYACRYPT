# System Design Diagrams (UML & Structural)

## 1. Software Requirements Specification (SRS) Summary
*   **Goal:** Provide an enterprise-grade web application for secure file encryption using the novel AryaCrypt algorithm.
*   **Functional Requirements:** User registration, secure login, file upload, file encryption, file decryption, metadata management, audit logging.
*   **Non-Functional Requirements:** High availability, stream-based I/O for large files (O(1) memory footprint), cryptographic latency < 2s for operations excluding actual encryption I/O.

## 2. Software Design Document (SDD) Summary
*   **Modularity:** Strict separation of UI, API, Cryptography, and Storage layers.
*   **Security:** Enforced HTTPS, PBKDF2 for password hashing, AES-256-GCM for files, stateless JWT authentication.

## 3. Use Case Diagram
```mermaid
flowchart LR
    User([User])
    Admin([System Admin])

    subgraph AryaCrypt System
        UC1(Register / Login)
        UC2(Upload File)
        UC3(Encrypt File via AryaCrypt)
        UC4(Decrypt File)
        UC6(View Analytics & Research Logs)
    end

    User --- UC1
    User --- UC2
    User --- UC3
    User --- UC4
    Admin --- UC6
```

## 4. Data Flow Diagram (DFD - Level 1)
```mermaid
flowchart TD
    User((User)) -->|Plaintext File & Password| P1[Process: AryaCrypt Engine]
    P1 -->|Encrypted File| Storage[(AWS S3 / File System)]
    P1 -->|Metadata: Salt, IV, Tag| DB[(PostgreSQL Database)]
    P1 -->|Encryption Metrics| Analytics[(Analytics Engine)]
    
    Storage -->|Encrypted File| P2[Process: Decryption Engine]
    DB -->|Metadata| P2
    User -->|Password| P2
    P2 -->|Plaintext File| User
```

## 5. Activity Diagram (Encryption Process)
```mermaid
stateDiagram-v2
    [*] --> UploadFile
    UploadFile --> ProvidePassword
    ProvidePassword --> GenerateSaltAndIV
    GenerateSaltAndIV --> RunAryabhataEncoding
    RunAryabhataEncoding --> RunPBKDF2
    RunPBKDF2 --> AESStreamEncryption
    AESStreamEncryption --> SaveMetadataToDB
    SaveMetadataToDB --> SaveCiphertextToStorage
    SaveCiphertextToStorage --> [*]
```

## 6. Component Diagram
```mermaid
flowchart TD
    subgraph Web Client
        UI[React UI]
    end

    subgraph API Gateway Layer
        Router[Express / FastAPI Router]
        Auth[JWT Middleware]
    end

    subgraph Core Cryptography Module
        AEE[Aryabhata Encoder]
        KDF[PBKDF2 Wrapper]
        AES[AES-GCM Streamer]
    end

    subgraph Data Layer
        DB[(PostgreSQL)]
        Blob[(Blob Storage)]
    end

    UI -->|REST/HTTP| Router
    Router --> Auth
    Auth --> AEE
    AEE --> KDF
    KDF --> AES
    AES --> Blob
    AES --> DB
```

## 7. Deployment Diagram
```mermaid
flowchart TD
    node1[User Device - Browser]
    
    subgraph Cloud Environment (e.g., AWS / Vercel + Railway)
        node2[Load Balancer / CDN]
        
        subgraph App Servers
            node3[Node.js / Python Backend Container]
        end
        
        subgraph Database Servers
            node4[(Managed PostgreSQL)]
        end
        
        subgraph Storage Servers
            node5[(S3 Object Storage)]
        end
    end

    node1 -->|HTTPS| node2
    node2 --> node3
    node3 -->|TCP/IP| node4
    node3 -->|HTTPS| node5
```
