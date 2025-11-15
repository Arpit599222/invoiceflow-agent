# InvoiceFlow – Simple Capstone Writeup

## What is my project?
InvoiceFlow is a simple invoice processing agent.  
It takes an invoice (file), extracts important details, saves them in a database, and starts an approval process.

## Problem
Finance teams spend too much time reading invoices, finding totals, and asking someone to approve them.  
This is slow and can cause mistakes.

## My Solution
I built a small multi-agent system that:

1. Reads invoice text (OCR agent – mocked)
2. Extracts important fields (Extraction agent – mocked)
3. Saves the invoice in a database (SQLite Memory)
4. Starts an approval workflow (Approval agent)
5. Can approve or reject invoices
6. Can export invoice data to CSV

## Agents I used
- **OCRAgent:** returns invoice text  
- **ExtractionAgent:** extracts vendor, invoice number, date, total, etc.  
- **ApprovalAgent:** handles approvals and reminders  
- **ManagerAgent:** controls all other agents  

## Concepts used from the course
- Multi-agent system  
- Custom tools (OCR + Extraction)  
- Long-running operations (reminders)  
- Memory (SQLite database)  
- Orchestration with ManagerAgent  

## Demo
I tested everything inside the Kaggle Notebook:
- processed invoice  
- extracted fields  
- saved to DB  
- approved invoice  
- exported CSV  

## GitHub Link
https://github.com/Arpit599222/invoiceflow-agent
