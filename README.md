# Pocket CFO Parser

## Overview
The **Pocket CFO Parser** is a lightweight, high‑performance tool designed for the Hira Prasad Welfare Foundation (HPWF) hackathon. It extracts financial data from PDFs, SMS messages, and GST filings, validates the information, and prepares it for downstream compliance and reporting workflows.

## Features
- **PDF parsing** to extract invoice details, GST numbers, and amounts.
- **SMS parsing** for transaction alerts and GST filing confirmations.
- **Validation** using Zod schemas to ensure data integrity.
- **Modular agents** for GST, PAN, and tax compliance logic.
- **CLI utilities** for quick data extraction and testing.
- **Extensible architecture** allowing additional parsers and agents.

## Tech Stack
- **Language:** Python 3.11
- **Parsing:** `pdfplumber`, `regex`
- **Validation:** `zod` via `pyzod`‑style schemas (custom implementation)
- **Testing:** `pytest`
- **CLI:** `argparse`
- **Packaging:** Standard `setuptools`

## Getting Started
1. **Prerequisites**
   - Python 3.11 or higher
   - Virtual environment (recommended)
2. **Setup**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
3. **Run the parser**
   ```bash
   python -m pocket_cfo_parser.parse_pdf <path-to-pdf>
   python -m pocket_cfo_parser.parse_sms <path-to-sms-file>
   ```
4. **Run tests**
   ```bash
   pytest
   ```

## Project Structure
```
.
├─ backend                # API server (FastAPI) for integration
├─ frontend               # Minimal UI for demoing the parser
├─ pocket_cfo_parser       # Core library
│   ├─ agents            # Agent implementations (GST, PAN, etc.)
│   ├─ models            # Data models & schemas
│   └─ utils             # Helper functions
├─ tests                 # Unit and integration tests
├─ requirements.txt      # Python dependencies
├─ start.bat             # Shortcut to launch development environment
└─ README.md             # Project documentation (this file)
```

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request. Ensure new code follows existing style guidelines, includes type hints, and passes all tests.

## License
This project is licensed under the MIT License – see the `LICENSE` file for details.

## Contact
- **Maintainer:** Pratik Gautam (pratik@gautam.dev)
- **GitHub:** https://github.com/PratikGautam-dev/hackfest
