"""
Bank PDF parsing module.

This module will handle the extraction of tabular financial data from bank statement
PDFs. It will utilize pdfplumber to read the document structure, parse rows of
transactions, and standardize them into Transaction objects.
"""
