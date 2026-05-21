# SmartDoc AI Agent

SmartDoc AI Agent is an intelligent terminal-based document assistant built using Python and Google Gemini API.

The assistant can read multiple TXT and PDF documents, answer contextual questions, perform mathematical calculations using tools, maintain conversation memory, and provide grounded responses with source citations.

---

# Features

- Multi-document querying
- TXT and PDF support
- AI agent behavior using tool calling
- Safe mathematical calculations
- Context-aware conversation memory
- Strict hallucination prevention
- Source citation support
- Continuous terminal interaction loop

---

# Technologies Used

- Python
- Google Gemini API
- pypdf
- colorama
- python-dotenv

---

# Project Structure

```bash
SmartDoc-AI-Agent/
│
├── documents/
│   ├── Employee_Details.txt
│   ├── AI_Project_Report.pdf
│
├── screenshots/
│
├── main.py
├── requirements.txt
├── README.md
└── explanation.txt
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/your-username/smartdoc-ai-agent.git
cd smartdoc-ai-agent
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure API Key

Create a `.env` file in the root directory.

```env
GEMINI_API_KEY=your_api_key_here
```

Get your Gemini API key from:

https://aistudio.google.com/app/apikey

---

# Add Documents

Place all `.txt` and `.pdf` files inside the `documents/` folder.

---

# Run Project

```bash
python main.py
```

---

# Example Questions

```text
Who wrote the employee report?

What did he work on?

What is the total budget?

Who developed the traffic monitoring system?

What accuracy was achieved?

What is the CEO phone number?
```

---

# Example Features Demonstrated

- Document-grounded responses
- Multi-turn contextual memory
- Safe calculation execution
- Missing information detection
- Source-aware answers

---

# Hallucination Prevention

The assistant is strictly grounded to uploaded documents and never uses external knowledge. If information is unavailable, it responds with:

```text
I could not find this information in the provided documents
```

---

# Author

Harshavardhan Veeralli

---

# License

This project is developed for educational and internship assessment purposes.
