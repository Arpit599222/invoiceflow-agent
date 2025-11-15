import asyncio

class OCRAgent:
    async def run(self, file_bytes: bytes):
        await asyncio.sleep(0.1)
        return """INVOICE
Vendor: Acme Supplies
Date: 2025-11-01
Invoice#: INV-12345
Total: 1,250.00
Currency: INR
"""
