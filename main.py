import asyncio, sqlite3, time, uuid, logging
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("invoiceflow")

async def mock_ocr(file_bytes: bytes) -> str:
    await asyncio.sleep(0.1)
    return """INVOICE
Vendor: Acme Supplies
Date: 2025-11-01
Invoice#: INV-12345
Total: 1,250.00
Currency: INR
"""

async def mock_llm_extract(text: str) -> Dict[str, str]:
    await asyncio.sleep(0.12)
    return {
        "vendor": "Acme Supplies",
        "invoice_number": "INV-12345",
        "date": "2025-11-01",
        "subtotal": "1000.00",
        "tax": "250.00",
        "total": "1250.00",
        "currency": "INR",
        "due_date": "2025-12-01"
    }

DB = "invoiceflow.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS invoices(id TEXT PRIMARY KEY, raw_text TEXT, vendor TEXT, invoice_number TEXT, date TEXT, subtotal TEXT, tax TEXT, total TEXT, currency TEXT, status TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY, invoice_id TEXT, approver TEXT, status TEXT, updated_at REAL)")
    conn.commit()
    conn.close()

def save_invoice(invoice_id: str, raw_text: str, fields: Dict[str,str]):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO invoices(id, raw_text, vendor, invoice_number, date, subtotal, tax, total, currency, status) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (invoice_id, raw_text, fields["vendor"], fields["invoice_number"], fields["date"], fields["subtotal"], fields["tax"], fields["total"], fields["currency"], "pending"))
    conn.commit()
    conn.close()

def list_invoices():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, vendor, invoice_number, date, total, currency, status FROM invoices ORDER BY rowid DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id":r[0],"vendor":r[1],"invoice_number":r[2],"date":r[3],"total":r[4],"currency":r[5],"status":r[6]} for r in rows]

def update_invoice_status(invoice_id: str, status: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE invoices SET status=? WHERE id=?", (status, invoice_id))
    conn.commit()
    conn.close()

def create_approval_record(approval_id, invoice_id, approver):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO approvals(id, invoice_id, approver, status, updated_at) VALUES(?,?,?,?,?)",
              (approval_id, invoice_id, approver, "pending", time.time()))
    conn.commit()
    conn.close()

def update_approval_status(approval_id, status):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE approvals SET status=?, updated_at=? WHERE id=?", (status, time.time(), approval_id))
    conn.commit()
    conn.close()

class IngestAgent:
    async def ingest(self, file_bytes: bytes):
        raw_text = await mock_ocr(file_bytes)
        fields = await mock_llm_extract(raw_text)
        invoice_id = str(uuid.uuid4())
        save_invoice(invoice_id, raw_text, fields)
        return invoice_id, fields

class ApprovalAgent:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.jobs = {}

    def start(self, invoice_id: str, approver: str, interval: int = 20):
        approval_id = str(uuid.uuid4())
        create_approval_record(approval_id, invoice_id, approver)
        def reminder():
            logger.info(f"Reminder: Invoice {invoice_id} pending approval by {approver}")
        job_id = str(uuid.uuid4())
        self.scheduler.add_job(reminder, "interval", seconds=interval, id=job_id)
        self.jobs[approval_id] = job_id
        return approval_id

    def complete(self, approval_id: str, status: str):
        job_id = self.jobs.get(approval_id)
        if job_id:
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass
            self.jobs.pop(approval_id, None)
        update_approval_status(approval_id, status)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT invoice_id FROM approvals WHERE id=?", (approval_id,))
        row = c.fetchone()
        conn.close()
        if row:
            invoice_id = row[0]
            update_invoice_status(invoice_id, status)

app = FastAPI()
init_db()

scheduler = BackgroundScheduler()
scheduler.start()

ingest_agent = IngestAgent()
approval_agent = ApprovalAgent(scheduler)

class ApprovalRequest(BaseModel):
    approval_id: str
    action: str

@app.post("/upload_invoice/")
async def upload_invoice(file: UploadFile = File(...)):
    content = await file.read()
    invoice_id, fields = await ingest_agent.ingest(content)
    approval_id = approval_agent.start(invoice_id, "approver@example.com")
    return {"invoice_id": invoice_id, "approval_id": approval_id, "extracted": fields}

@app.get("/invoices/")
def invoices():
    return {"invoices": list_invoices()}

@app.post("/approve/")
def approve(req: ApprovalRequest):
    if req.action not in ("approved", "rejected"):
        raise HTTPException(400, "Action must be approved or rejected")
    approval_agent.complete(req.approval_id, req.action)
    return {"status": "OK", "approval_id": req.approval_id, "action": req.action}

@app.get("/")
def home():
    return {"message": "InvoiceFlow API running"}

