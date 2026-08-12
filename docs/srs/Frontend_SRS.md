# Frontend Software Requirements Specification (SRS)

## 1. Introduction
The frontend of AryaCrypt is designed to provide an enterprise-grade, secure, and user-friendly interface for file encryption utilizing the novel Aryabhata-based cryptographic framework.

## 2. Functional Requirements
*   **FR-1: User Authentication:**
    *   Users must be able to securely register and log into the system.
    *   The frontend must handle session management via stateless JWT tokens.
*   **FR-2: File Upload & Chunking:**
    *   The interface must allow users to select large files for encryption.
    *   The frontend must utilize the HTML5 File API to process files in stream-based chunks to ensure an O(1) memory footprint and prevent browser crashes on multi-gigabyte files.
*   **FR-3: Encryption & Decryption Triggers:**
    *   The UI must provide clear actions to encrypt and decrypt files.
    *   Passwords/keys must be securely captured and transmitted to the backend.
*   **FR-4: Dashboards and Analytics:**
    *   The application must include a dashboard for administrators and researchers to view encryption metrics, latency logs, and audit trails.

## 3. Non-Functional Requirements
*   **NFR-1: Security:** All data transmission must occur over HTTPS. The frontend must implement client-side validation to prevent basic injection attacks and ensure data integrity before backend submission.
*   **NFR-2: Usability:** The interface must be highly responsive and accessible, providing clear visual feedback during long-running encryption tasks.
*   **NFR-3: Performance:** Cryptographic initiation operations (excluding the actual file I/O latency) must feel instantaneous (under 2 seconds UI response).
