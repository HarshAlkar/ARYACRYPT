# Frontend System Diagrams

## 1. High-Level Component Flow

```mermaid
flowchart TD
    subgraph Web Client
        UI[React UI / Tailwind CSS]
        State[State Management / Auth Context]
        Service[API Service Layer]
    end

    subgraph Backend Services
        Router[API Gateway]
    end

    UI --> State
    UI --> Service
    Service -->|REST/HTTPS| Router
```

## 2. File Upload & Processing Activity

```mermaid
stateDiagram-v2
    [*] --> SelectFile
    SelectFile --> ValidateSizeAndType
    ValidateSizeAndType --> ProvidePassword
    ProvidePassword --> InitiateChunking
    
    state InitiateChunking {
        ReadChunk --> SendToBackend
        SendToBackend --> UpdateProgressUI
        UpdateProgressUI --> ReadChunk
    }
    
    InitiateChunking --> ReceiveEncryptedBlob
    ReceiveEncryptedBlob --> DownloadCiphertext
    DownloadCiphertext --> [*]
```

## 3. Deployment Architecture (Frontend)

```mermaid
flowchart TD
    User[User Browser]
    
    subgraph Edge Network
        CDN[Content Delivery Network / Vercel / Cloudflare]
    end
    
    subgraph Backend
        API[Backend Load Balancer]
    end
    
    User -->|Requests Static Assets| CDN
    User -->|API Calls (HTTPS)| API
```
