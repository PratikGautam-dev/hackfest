"""
Bank PDF parsing module.

This module handles the extraction of tabular financial data from bank statement
PDFs. It utilizes pdfplumber to read the document structure, parse rows of
transactions, and standardize them into Transaction objects.
"""

import logging
import re
import pdfplumber
from dateutil import parser as date_parser
from pocket_cfo_parser.models.transaction import Transaction

logger = logging.getLogger(__name__)


def _safe_amount(value: str) -> float:
    if not value or not value.strip():
        return 0.0
    try:
        return float(value.replace(',', '').strip())
    except ValueError:
        return 0.0


def parse_pdf(filepath: str) -> list[Transaction]:
    """
    Parses a bank statement PDF and returns a list of Transaction objects.
    Using pdfplumber, it extracts tables and handles variations in bank formats like HDFC & SBI.
    """
    transactions = []
    
    with pdfplumber.open(filepath) as pdf:
        if not pdf.pages:
            return transactions
            
        first_page_text = pdf.pages[0].extract_text() or ""
        bank_name = "Unknown"
        if "HDFC" in first_page_text:
            bank_name = "HDFC"
        elif "State Bank of India" in first_page_text or "SBI" in first_page_text:
            bank_name = "SBI"
        
        logger.info(f"Detected bank: {bank_name} — parsing {len(pdf.pages)} page(s)")
            
        for page_num, page in enumerate(pdf.pages):
            table = page.extract_table()
            if not table:
                logger.debug(f"Page {page_num + 1}: no table found, skipping")
                continue
                
            for row in table:
                if not row or len(row) < 3:
                    continue
                    
                row_cleaned = [cell.strip() if cell else "" for cell in row]
                first_cell = row_cleaned[0].lower()
                
                if "date" in first_cell or "txn" in first_cell or "description" in first_cell:
                    continue
                    
                try:
                    date_str = row_cleaned[0]
                    description_str = row_cleaned[1]
                    debit_str = row_cleaned[2] if len(row_cleaned) > 2 else ""
                    credit_str = row_cleaned[3] if len(row_cleaned) > 3 else ""
                    
                    if not date_str or len(date_str) < 5:
                        continue
                        
                    if not debit_str and not credit_str:
                        continue

                    txn_date = date_parser.parse(date_str, dayfirst=True)
                    
                    raw_text = description_str
                    confidence = 0.95
                    original_desc = description_str
                    
                    description_str = re.sub(r'\b\d{6,15}\b', '', description_str)
                    description_str = re.sub(r'(?i)^(UPI|NEFT|IMPS|ACH|REV|NFET|Info)[/:-]\s?', '', description_str)
                    description_str = description_str.replace('/', ' ').replace('-', ' ').strip()
                    description_str = re.sub(r'(?i)\b(upi|credit|debit)\b', '', description_str)
                    description_str = re.sub(r'\s+', ' ', description_str).strip()
                    party = description_str.title() or "Unknown"
                    
                    if len(original_desc) - len(party) > 15 or party == "Unknown":
                        confidence = 0.6

                    debit_amount = _safe_amount(debit_str)
                    credit_amount = _safe_amount(credit_str)

                    if debit_amount > 0:
                        amount, txn_type = debit_amount, "debit"
                    elif credit_amount > 0:
                        amount, txn_type = credit_amount, "credit"
                    else:
                        continue
                        
                    transaction = Transaction(
                        amount=amount,
                        type=txn_type,  # type: ignore
                        party=party,
                        date=txn_date,
                        source="pdf",
                        raw_text=raw_text,
                        confidence=confidence
                    )
                    transactions.append(transaction)
                        
                except Exception as e:
                    logger.warning(f"Skipped PDF row {row_cleaned}: {type(e).__name__}: {e}")
                    continue
                    
    logger.info(f"PDF parse complete: extracted {len(transactions)} transactions from {filepath}")
    return transactions

