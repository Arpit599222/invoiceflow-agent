# InvoiceFlow – Enterprise Invoice Processing Agent

InvoiceFlow is an AI-driven multi-agent system designed to automate invoice processing, extraction, and approval workflows.

## 🚀 Features
- OCR Agent – extracts text from invoice files  
- Extraction Agent – extracts structured fields (vendor, date, total, etc.)  
- Approval Agent – creates approval workflow with reminders  
- Manager Agent – orchestrates the full pipeline  
- SQLite-based memory for invoices and approval logs

## 📄 Notebook
The entire working enterprise agent is inside the Kaggle notebook:
- Invoice ingestion
- Multi-agent execution
- Data extraction
- Database updates
- CSV export
- Approvals (approve/reject)

## 🧠 Technologies
- Python  
- FastAPI (optional)  
- APScheduler  
- SQLite  
- Asyncio agents  
- Kaggle Notebook runtime  

## 📊 Demo Output
The system successfully:
- Processes invoices  
- Extracts fields  
- Saves entries to the database  
- Sends approval reminders  
- Marks approvals  
- Exports CSV  

## 🏆 Kaggle Capstone Project
This repository is used as the submission for the Kaggle 5-Day AI Agents Intensive Capstone Challenge.
