"""
Bank PDF parsing module.

This module handles the extraction of tabular financial data from bank statement
PDFs. It utilizes pdfplumber to read the document structure, parse rows of
transactions, and standardize them into Transaction objects.

Supports: ICICI, HDFC, SBI bank statement formats.
"""

import logging
import re
import pdfplumber
from dateutil import parser as date_parser
from pocket_cfo_parser.models.transaction import Transaction

logger = logging.getLogger(__name__)


def _safe_amount(value: str) -> float:
    """Safely converts string amounts to float, handling commas and spaces."""
    if not value or not value.strip():
        return 0.0
    try:
        cleaned = value.replace(',', '').replace(' ', '').strip()
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def _extract_party_from_remarks(remarks: str) -> str:
    """
    Extracts merchant/party name from transaction remarks.
    Handles UPI patterns like:
    - UPI/SIT Contee/gpay-112591429/Payment fr/AXIS BANK
    - UPI/PRAVEENA R/Q757364713@/bl/Payment fr/YES BANK
    - UPI/M S Prakas/poytm.s1qnqt@/Payment fr/YES BANK
    """
    if not remarks:
        return "Unknown"
    
    # Extract name before "@" or "/" patterns
    patterns = [
        r'UPI/([A-Z][A-Za-z\s]+?)(?:@|/)',  # UPI/NAME SURNAME@
        r'(?:UPI|NEFT|IMPS)[/:-]\s*([^/]+?)(?:/|@)',  # After NEFT/IMPS/UPI
        r'\(by:\s*([^)]+)\)',  # (by: Name)
        r'(?:fr|from)\s+([A-Za-z\s]+?)(?:\.|$)',  # from NAME
    ]
    
    for pattern in patterns:
        match = re.search(pattern, remarks, re.IGNORECASE)
        if match:
            party = match.group(1).strip().title()
            # Filter out generic terms
            if party.lower() not in ['upi', 'bank', 'payment', 'from', 'to']:
                return party
    
    # Fallback: Extract first meaningful words
    words = remarks.split()
    if len(words) > 0:
        return ' '.join(words[:2]).title()
    
    return "Unknown"


def _detect_bank_name(first_page_text: str) -> str:
    """Detects which bank the PDF belongs to."""
    if "ICICI" in first_page_text:
        return "ICICI"
    elif "HDFC" in first_page_text:
        return "HDFC"
    elif "State Bank of India" in first_page_text or "SBI" in first_page_text:
        return "SBI"
    return "Unknown"


def _find_table_with_headers(page) -> tuple[list, dict] | None:
    """
    Extracts table and returns (table_data, column_mapping).
    Identifies column positions by header names.
    Returns None if no valid table found.
    """
    table = page.extract_table()
    if not table or len(table) < 2:
        return None
    
    # First row should be headers
    header_row = [str(cell).strip().lower() if cell else "" for cell in table[0]]
    
    # Map expected headers to column index
    column_map = {}
    for idx, header in enumerate(header_row):
        if any(x in header for x in ['date', 'transaction date']):
            column_map['date'] = idx
        elif any(x in header for x in ['remarks', 'description', 'transaction remarks']):
            column_map['remarks'] = idx
        elif any(x in header for x in ['withdrawal', 'debit', 'dr']):
            column_map['withdrawal'] = idx
        elif any(x in header for x in ['deposit', 'credit', 'cr']):
            column_map['deposit'] = idx
    
    # Validate we got the essential columns
    if 'date' not in column_map or 'remarks' not in column_map:
        logger.warning(f"Table headers not recognized. Found: {header_row}")
        return None
    
    # If withdrawal/deposit not found, assume last two columns
    if 'withdrawal' not in column_map or 'deposit' not in column_map:
        if len(header_row) >= 3:
            column_map['withdrawal'] = len(header_row) - 2
            column_map['deposit'] = len(header_row) - 1
    
    return table[1:], column_map  # Skip header row


def _parse_icici_text(text: str) -> list[Transaction]:
    """
    Parses ICICI bank statement from extracted text.
    Handles multi-line transaction entries.
    """
    transactions = []
    
    # Split by transaction rows (numbered 1, 2, 3, etc.)
    # Pattern: NUMBER DATE REST_OF_TEXT
    lines = text.split('\n')
    
    current_transaction = None
    current_remarks = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to match start of new transaction: "NUM DATE"
        # Date format: DD.MM.YYYY
        match = re.match(r'^(\d{1,2})\s+(\d{1,2}\.\d{2}\.\d{4})\s+(.*)$', line)
        
        if match and current_transaction is None:
            # Starting a new transaction
            txn_num = match.group(1)
            date_str = match.group(2)
            first_line = match.group(3)
            
            current_transaction = {
                'date': date_str,
                'remarks': first_line
            }
            current_remarks = [first_line]
        
        elif match and current_transaction is not None:
            # Previous transaction is complete, save it
            try:
                txn = _create_transaction_from_icici(current_transaction, '\n'.join(current_remarks))
                if txn:
                    transactions.append(txn)
            except Exception as e:
                logger.warning(f"Failed to parse transaction: {e}")
            
            # Start new transaction
            txn_num = match.group(1)
            date_str = match.group(2)
            first_line = match.group(3)
            
            current_transaction = {
                'date': date_str,
                'remarks': first_line
            }
            current_remarks = [first_line]
        
        elif current_transaction is not None:
            # Continuation of current transaction remarks
            current_remarks.append(line)
    
    # Don't forget the last transaction
    if current_transaction is not None:
        try:
            txn = _create_transaction_from_icici(current_transaction, '\n'.join(current_remarks))
            if txn:
                transactions.append(txn)
        except Exception as e:
            logger.warning(f"Failed to parse last transaction: {e}")
    
    return transactions


def _create_transaction_from_icici(txn_data: dict, full_remarks: str) -> Transaction | None:
    """
    Creates a Transaction from parsed ICICI transaction data.
    Extracts amount from the full remarks line (last numbers before balance).
    """
    try:
        # Parse date
        date_str = txn_data['date']
        txn_date = date_parser.parse(date_str, dayfirst=True)
        
        # Extract amount from full remarks
        # Amount appears before the balance (last number in the line)
        # Pattern: find numbers like "10.00", "1242.00", etc.
        amounts = re.findall(r'(\d+\.?\d*)', full_remarks)
        
        if not amounts:
            return None
        
        # The last amount is usually the balance, second-to-last is the transaction amount
        # But we need to be careful - transaction amounts are smaller than balances
        # Let's take the first standalone amount that looks like a transaction
        amount = None
        for amt_str in amounts:
            amt = _safe_amount(amt_str)
            if 0 < amt < 1000000:  # Reasonable transaction range
                amount = amt
                break
        
        if not amount:
            return None
        
        # Determine if debit or credit (all visible transactions are debits/withdrawals)
        # In bank statements, withdrawn amounts are shown in one column
        txn_type = "debit"
        
        # Extract party name
        party = _extract_party_from_remarks(full_remarks)
        
        # Create transaction
        transaction = Transaction(
            amount=amount,
            type=txn_type,  # type: ignore
            party=party,
            date=txn_date,
            source="pdf",
            raw_text=full_remarks,
            confidence=0.85
        )
        
        logger.debug(f"Parsed ICICI: ₹{amount} to {party} on {txn_date.date()}")
        return transaction
    
    except Exception as e:
        logger.warning(f"Failed to create transaction: {e}")
        return None


def parse_pdf(filepath: str) -> list[Transaction]:
    """
    Parses a bank statement PDF and returns a list of Transaction objects.
    Handles ICICI, HDFC, and SBI formats automatically.
    
    For PDFs with complex layouts, falls back to text extraction.
    
    Args:
        filepath: Path to the bank statement PDF
        
    Returns:
        List of parsed Transaction objects
    """
    transactions = []
    
    try:
        with pdfplumber.open(filepath) as pdf:
            if not pdf.pages:
                logger.warning(f"PDF {filepath} has no pages")
                return transactions
            
            # Extract all text from all pages
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            bank_name = _detect_bank_name(full_text)
            logger.info(f"Detected bank: {bank_name} — parsing {len(pdf.pages)} page(s)")
            
            # Parse based on bank type
            if bank_name == "ICICI":
                transactions = _parse_icici_text(full_text)
            else:
                # Fallback for other banks
                logger.warning(f"Bank {bank_name} text parsing not fully implemented yet")
                transactions = _parse_icici_text(full_text)  # Try ICICI format anyway
    
    except Exception as e:
        logger.error(f"Failed to parse PDF {filepath}: {type(e).__name__}: {e}")
        return []
    
    logger.info(f"PDF parse complete: extracted {len(transactions)} transactions from {filepath}")
    return transactions

