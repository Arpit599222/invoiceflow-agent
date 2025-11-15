import uuid
from typing import Dict, List
from .ocr_agent import OCRAgent
from .extraction_agent import ExtractionAgent
from .approval_agent import ApprovalAgent
from .memory import save_invoice, list_invoices

class ManagerAgent:
    def __init__(self, scheduler):
        self.ocr_agent = OCRAgent()
        self.extraction_agent = ExtractionAgent()
        self.approval_agent = ApprovalAgent(scheduler)

    async def process_invoice(self, file_bytes: bytes):
        raw_text = await self.ocr_agent.run(file_bytes)
        fields = await self.extraction_agent.run(raw_text)
        invoice_id = str(uuid.uuid4())
        save_invoice(invoice_id, raw_text, fields)
        approval_id = self.approval_agent.start(invoice_id, "approver@example.com")
        return invoice_id, approval_id, fields

    def invoices(self):
        return list_invoices()
