import time
import uuid
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler

class ApprovalAgent:
    def __init__(self, scheduler=None):
        self.scheduler = scheduler or BackgroundScheduler()
        if not self.scheduler.running:
            self.scheduler.start()
        self.jobs = {}

    def _create_approval_record(self, approval_id, invoice_id, approver):
        conn = sqlite3.connect("invoiceflow.db")
        c = conn.cursor()
        c.execute("INSERT INTO approvals(id, invoice_id, approver, status, updated_at) VALUES(?,?,?,?,?)",
                  (approval_id, invoice_id, approver, "pending", time.time()))
        conn.commit()
        conn.close()

    def _update_approval_record(self, approval_id, status):
        conn = sqlite3.connect("invoiceflow.db")
        c = conn.cursor()
        c.execute("UPDATE approvals SET status=?, updated_at=? WHERE id=?", (status, time.time(), approval_id))
        conn.commit()
        conn.close()

    def _update_invoice_status(self, invoice_id, status):
        conn = sqlite3.connect("invoiceflow.db")
        c = conn.cursor()
        c.execute("UPDATE invoices SET status=? WHERE id=?", (status, invoice_id))
        conn.commit()
        conn.close()

    def start(self, invoice_id: str, approver: str, interval: int = 20):
        approval_id = str(uuid.uuid4())
        self._create_approval_record(approval_id, invoice_id, approver)

        def reminder():
            print(f"Reminder: Invoice {invoice_id} pending approval by {approver}")

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

        self._update_approval_record(approval_id, status)

        conn = sqlite3.connect("invoiceflow.db")
        c = conn.cursor()
        c.execute("SELECT invoice_id FROM approvals WHERE id=?", (approval_id,))
        row = c.fetchone()
        conn.close()

        if row:
            invoice_id = row[0]
            self._update_invoice_status(invoice_id, status)
