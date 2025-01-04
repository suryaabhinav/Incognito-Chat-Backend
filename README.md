# Incognito Chat Backend

**Incognito Chat Backend** is the core server-side application powering the **Incognito Chat** AI chatbot. Built with Python and FastAPI, this backend integrates a locally hosted Large Language Model (LLM) for conversational AI while prioritizing user privacy and security. With features like conversational memory, real-time web scraping, and secure communication protocols, the backend ensures rich, context-aware interactions within a completely private environment.

---

## Table of Contents

- [Project Description](#project-description)  
- [Features](#features)  
- [Technology Stack](#technology-stack)  
- [Getting Started](#getting-started)  
    - [Prerequisites](#prerequisites)  
    - [Installation](#installation)  
    - [Running the Server](#running-the-server)  
- [Usage](#usage)  
- [Security Features](#security-features)  
- [License](#license)  

---

## Project Description

The backend server for **Incognito Chat** is designed to support private, secure, and intelligent chatbot interactions. The system leverages a locally hosted Llama 3 model for language processing, ensuring no data leaves the local environment. Enhanced by web scraping and real-time data fetching, the chatbot delivers context-aware responses enriched with internet-based information.

By combining VPN tunneling, JWT-based authentication, and encrypted WebSocket communication, the backend ensures secure cross-device compatibility over a self-hosted network.

---

## Features

1. **Locally Hosted AI:**  
   - Integrates Llama 3 as the locally hosted LLM for conversational AI.  
   - Ensures complete data privacy with no reliance on cloud-based services.  

2. **Conversational Memory:**  
   - Implements memory management for maintaining conversational context.  

3. **Real-time Data Enrichment:**  
   - Uses web scraping and real-time data fetching to provide context-aware responses.  

4. **Secure Communication:**  
   - Combines VPN tunneling, JWT-based authentication, and encrypted WebSockets for secure, real-time interactions.  

5. **Cross-device Compatibility:**  
   - Accessible via devices connected to the local network through the WireGuard VPN.  

---

## Technology Stack

- **Programming Language:** Python 3.12.7  
- **Framework:** FastAPI  
- **LLM Integration:** Llama 3 (Locally hosted)  
- **Security:**  
  - WireGuard VPN for secure API exposure.  
  - JWT for API authentication.  
  - Encrypted WebSocket protocols for real-time communication.  
- **Web Scraping:** Beautiful Soup, Requests  
- **Data Storage:** In-memory storage for conversational memory management (with extensibility options).  

---

## Getting Started

### Prerequisites

To set up the backend, ensure the following:

- **Python 3.12.7** installed on your system.  
- **WireGuard VPN** installed and configured for secure API exposure.  
- **Virtual Environment Tools** (e.g., `venv` or `virtualenv`).  
- **Dependencies:**  
  - FastAPI  
  - Uvicorn  
  - PyJWT  
  - Beautiful Soup  
  - Requests  
  - Any required libraries for the Llama 3 model.  

### Installation

1. **Clone the repository:**  
   ```bash
   git clone <repository_url>
   cd incognito-chat-backend
   ```
2. Set up a virtual environment:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure the WireGuard VPN:
- Set up a WireGuard server to securely expose the backend API.
- Share client configuration files to connect devices securely.

5. Set environment variables:

    Create a `.env` file to store sensitive information like JWT secret keys:
    ```env
    JWT_SECRET_KEY=your_secret_key
    ```

### Running the Server

- Check the IP address:

    ```bash
    ifconfig    # On Windows: ipconfig
    # Ex: 192.168.0.1
    ```

- Start the FastAPI server with Uvicorn:

    ```bash
    uvicorn main:app --host 192.168.0.1 --port 8000 --reload
    ```
- Test the server locally or over the VPN by navigating to:

    http://192.15.0.1:8000/

---

## Usage

- **API Endpoints**:

    The backend provides the following key endpoints:

    - `/ws/chatproxyrequest`: For sending and receiving chat messages.
    - `/reset`: To clear the conversational memory and start fresh.
    - `/generatetoken`: To generate the JWT token to access the API
    

- **Interacting with the Backend**:

    - The SwiftUI-based frontend communicates with the backend via API and WebSocket protocols for real-time messaging.
    - Authentication is required for API access using JWT tokens.
    

---

## Security Features

1. **VPN Tunneling with WireGuard**:

    Ensures the backend API is securely exposed only to authorized devices on the network.

2. **JWT Authentication**:

    Provides a secure mechanism for verifying API access.

3. **Encrypted WebSockets**:

    Protects real-time data transfer from interception.

4. **Local-only Processing**:

    Keeps all user data within the local network by avoiding cloud services.

---

## License

This project is licensed under the MIT License.

- **Permission**:

    You are free to download, modify, and use this backend for personal or professional purposes.

- **Restriction**:

    Modifications to the original repository are not permitted.

- **Disclaimer**:

    This project is provided "as is," without warranty of any kind. Use it at your own risk.

For the full license text, see the LICENSE file in the repository.

---

## Contributing

Contributions to enhance functionality or security are welcome! Before contributing:

- Test your changes thoroughly.
- Adhere to coding standards and best practices.

For issues or feature requests, open an issue in the repository.

---

Secure and private chatbot interactions made possible with **Incognito Chat Backend!** 🚀
