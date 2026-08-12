# Frontend Architecture Document

## 1. Architectural Style
The frontend follows a modern Single Page Application (SPA) architecture, heavily decoupled from the backend cryptographic and storage layers. It communicates entirely via RESTful APIs.

## 2. Technology Stack
*   **Core Framework:** React.js bootstrapped with Vite for rapid compilation and optimized builds.
*   **Language:** TypeScript for strict type-checking and improved developer experience.
*   **Styling:** Tailwind CSS for utility-first responsive styling.
*   **UI Components:** Shadcn UI for accessible, customizable, and high-quality UI primitives.

## 3. Layer Separation
*   **Presentation Layer:** React components responsible for rendering the UI and capturing user input.
*   **State Management:** React Context or a lightweight state manager (e.g., Zustand) to manage authentication state and file processing progress.
*   **Service/API Layer:** Abstracted service classes responsible for making HTTP requests (using `fetch` or `axios`) to the Node.js/Python backend gateway.

## 4. File Processing Architecture
To handle the requirement of encrypting large files without memory overflow:
1.  **Selection:** User selects a file via standard `<input type="file">`.
2.  **Chunking:** The frontend reads the file in chunks (e.g., 4MB slices) using the `File.slice()` API.
3.  **Streaming (Optional/Backend dependent):** The frontend streams these chunks to the backend API incrementally rather than loading the entire file into the browser's RAM.

## 5. Security Architecture
*   **Stateless Authentication:** JWTs are stored securely (preferably in HttpOnly cookies, or localized secure storage) and attached to the `Authorization` header of outgoing requests.
*   **Input Sanitization:** TypeScript and React inherently protect against XSS, but explicit validation (e.g., using Zod) should be applied to all forms before submission.
