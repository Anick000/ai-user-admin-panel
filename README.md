# AI User Admin Panel

An AI-powered user management system built using **FastAPI, MCP tools, and LLM agents**.

Users can manage accounts using natural language commands through an AI dashboard.

Example commands:

- create a user named Rahul with email rahul@gmail.com
- show all users
- update Rahul email to rahul123@gmail.com
- delete Rahul

---

## Architecture

Frontend Dashboard  
↓  
FastAPI API  
↓  
AI Agent  
↓  
Groq LLM  
↓  
MCP Client  
↓  
MCP Server Tools  

---

## Features

- Natural language user management
- AI tool calling using LLM
- MCP protocol integration
- ChatGPT-style admin dashboard
- Name → user_id resolution automatically
- Create / Read / Update / Delete users

---

## Tech Stack

- FastAPI
- Python
- Groq LLM
- MCP (Model Context Protocol)
- HTML / CSS / JS dashboard

---

## Installation

Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-user-admin-panel.git
cd ai-user-admin-panel