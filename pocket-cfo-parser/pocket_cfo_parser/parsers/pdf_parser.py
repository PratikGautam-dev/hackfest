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

# Set up logging for warnings when parsing rows
logger = logging.getLogger(__name__)

def parse_pdf(filepath: str) -> list[Transaction]:
    """
    Parses a bank statement PDF and returns a list of Transaction objects.
    Using pdfplumber, it extracts tables and handles variations in bank formats like HDFC & SBI.
    """
    transactions = []
    
    # 1. Use pdfplumber to open the PDF at the given filepath
    with pdfplumber.open(filepath) as pdf:
        if not pdf.pages:
            return transactions
            
        # 2. Detect which bank the statement belongs to by checking first page text
        first_page_text = pdf.pages[0].extract_text() or ""
        bank_name = "Unknown"
        if "HDFC" in first_page_text:
            bank_name = "HDFC"
        elif "State Bank of India" in first_page_text or "SBI" in first_page_text:
            bank_name = "SBI"
            
        # 3. Extract the transaction table from each page
        for page in pdf.pages:
            # Note: extract_table() gets the largest table by default
            # For complex multi-table PDFs, extract_tables() might be needed,
            # but for simple statements, extract_table() gives the main one.
            table = page.extract_table()
            if not table:
                continue
                
            for row in table:
                # Make sure the row has enough columns for date, desc, debit, credit
                if not row or len(row) < 4:
                    continue
                    
                # Clean up extracted string cells
                row_cleaned = [cell.strip() if cell else "" for cell in row]
                first_cell = row_cleaned[0].lower()
                
                # 4. Skip header rows
                if "date" in first_cell or "txn" in first_cell or "description" in first_cell:
                    continue
                    
                # 5. Process row with try/except
                try:
                    date_str = row_cleaned[0]
                    description_str = row_cleaned[1]
                    debit_str = row_cleaned[2]
                    credit_str = row_cleaned[3]
                    
                    # Sanity check: Date strings should at least be long enough
                    if not date_str or len(date_str) < 5:
                        continue
                        
                    # Skip rows where both debit and credit columns are empty (balance-only rows)
                    if not debit_str and not credit_str:
                        continue
                        
                    # --- Extract Date ---
                    # use dateutil.parser.parse with dayfirst=True
                    txn_date = date_parser.parse(date_str, dayfirst=True)
                    
                    # --- Extract Description/Party ---
                    raw_text = description_str
                    confidence = 0.95
                    
                    # Strip out UPI reference numbers (sequences of digits typically 6+ chars)
                    original_desc = description_str
                    description_str = re.sub(r'\b\d{6,15}\b', '', description_str)
                    
                    # Strip common technical prefixes the banks add 
                    # e.g., "UPI/...", "REV/...", "ACH/...", "NEFT/..."
                    description_str = re.sub(r'(?i)^(UPI|NEFT|IMPS|ACH|REV|NFET|Info)[/:-]\s?', '', description_str)
                    
                    # Replace remaining structural slashes and hyphens with spaces
                    description_str = description_str.replace('/', ' ').replace('-', ' ').strip()
                    
                    # Strip lingering "UPI" or "Credit" text
                    description_str = re.sub(r'(?i)\b(upi|credit|debit)\b', '', description_str)
                    
                    # Clean up extra whitespace and title-case the party
                    description_str = re.sub(r'\s+', ' ', description_str).strip()
                    party = description_str.title()
                    
                    if not party:
                        party = "Unknown"
                        
                    # If heavily modified or guessed, lower confidence
                    if len(original_desc) - len(party) > 15 or party == "Unknown":
                        confidence = 0.6
                        
                    # --- Extract Amount and Type ---
                    amount = 0.0
                    txn_type = None
                    
                    if debit_str:
                        # Third column is debit
                        amount = float(debit_str.replace(',', ''))
                        txn_type = "debit"
                    elif credit_str:
                        # Fourth column is credit
                        amount = float(credit_str.replace(',', ''))
                        txn_type = "credit"
                        
                    if amount > 0:
                        # 6. Generate Transaction Object
                        # Source is "pdf"
                        transaction = Transaction(
                            amount=amount,
                            type=txn_type, # type: ignore
                            party=party,
                            date=txn_date,
                            source="pdf",
                            raw_text=raw_text,
                            confidence=confidence
                        )
                        transactions.append(transaction)
                        
                except Exception as e:
                    # 7. Log warning and skip bad rows instead of crashing
                    logger.warning(f"Failed to parse PDF row {row_cleaned} in {filepath}: {str(e)}")
                    continue
                    
    return transactions
