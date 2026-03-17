# AI User Admin Panel

An AI-powered user management system built using **FastAPI, MCP tools, and LLM agents**.

Users can manage accounts using natural language commands through an AI dashboard.

---

## ✨ Features

- Natural language user management
- AI tool calling using LLM
- MCP protocol integration
- ChatGPT-style admin dashboard UI
- Name → user_id resolution automatically
- Full CRUD operations (Create, Read, Update, Delete)

---

## 🧠 Architecture

Frontend Dashboard  
↓  
FastAPI Backend (Port 8000)  
↓  
AI Agent  
↓  
Groq LLM  
↓  
MCP Client  
↓  
MCP Server (Port 8001)  
↓  
User Tools  

---

## 🛠 Tech Stack

- FastAPI
- Python
- Groq LLM
- MCP (Model Context Protocol)
- HTML / CSS / JavaScript

---

## 🚀 Installation & Setup
1. Clone the repository
    git clone https://github.com/YOUR_USERNAME/ai-user-admin-panel.git
    cd ai-user-admin-panel
    
2. Install dependencies
   pip install -r requirements.txt
   
🔐 API Key Setup- You can set your Groq API key in two ways:

Option 1 (Recommended): .env file
    Create a file named .env in the root folder:
    GROQ_API_KEY=your_groq_api_key_here
    
Option 2: Environment variable
    Windows (PowerShell)
    setx GROQ_API_KEY "your_key_here"  
    Restart terminal after this.

Mac/Linux
    export GROQ_API_KEY="your_key_here"

    
▶️ Running the Project
⚠️ Make sure to run BOTH servers in separate terminals.

Step 1: Start MCP Server
    python -m uvicorn app.mcp.mcp_server:app --port 8001 --reload
    Runs on:
    http://127.0.0.1:8001

Step 2: Start FastAPI Backend
    python -m uvicorn app.main:app --reload
    Runs on:
    http://127.0.0.1:8000
      
    Swagger UI:
    http://127.0.0.1:8000/docs

Step 3: Open Dashboard
    Open the file: dashboard.html in your browser.

💬 Example Commands
Try these in the dashboard:
    create a user named Rahul with email rahul@gmail.com
    show all users
    update Rahul email to rahul123@gmail.com
    delete Rahul


📌 Notes
    Data is stored in-memory (resets when server restarts)
    MCP server handles tool execution
    AI agent converts prompts → structured tool calls
