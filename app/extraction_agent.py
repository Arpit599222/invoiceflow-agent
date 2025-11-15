import asyncio

class ExtractionAgent:
    async def run(self, text: str):
        await asyncio.sleep(0.05)
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
