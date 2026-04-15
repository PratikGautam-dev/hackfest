"""
Data Seeding Pipeline
Dynamically populates local MongoDB constraints structurally bridging the demo dashboard explicitly.
"""

import os
import sys

# Ensure project root natively handles absolute execution bounding strings reliably
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocket_cfo_parser.ingestion import ingest_batch_sms, ingest_pdf
from pocket_cfo_parser.db.mongo import save_user, users_collection
from tests.test_data.sample_sms import SAMPLE_SMS

def seed_demo_data():
    print(">>> Initializing Hackathon Seeding Matrix...")
    
    # Enforce safe mathematical idempotency explicitly wiping isolated parameters
    users_collection.delete_many({"name": "Demo Business"})
    print("[-] Cleared pre-existing mock demo structures native bounds.")
    
    # Establish base boundaries creating proper identification constraints 
    user_id = save_user("Demo Business", "9876543210", "Sharma General Traders")
    print(f"[+] Instantiated Demo Profile logically mapping into ID: {user_id}")
    
    # 1. Pipeline Unstructured Text Constraints securely natively
    print(f"[*] Dispatching sequential SMS logic matrices natively...")
    sms_txns = ingest_batch_sms(SAMPLE_SMS, user_id)
    print(f"[+] Successfully structured {len(sms_txns)} textual occurrences globally.")
    
    # 2. Pipeline Multi-modal Document Parameters explicitly structurally
    print(f"[*] Booting PDF tabular arrays seamlessly extracting parameters...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hdfc_path = os.path.join(base_dir, "tests", "test_data", "hdfc_statement.pdf")
    sbi_path = os.path.join(base_dir, "tests", "test_data", "sbi_statement.pdf")
    
    if os.path.exists(hdfc_path):
        hdfc_txns = ingest_pdf(hdfc_path, user_id)
        print(f"[+] HDFC engine natively extracted {len(hdfc_txns)} document records securely.")
    else:
        print(f"[!] Target natively unstructured: {hdfc_path} failed to locate.")
        
    if os.path.exists(sbi_path):
        sbi_txns = ingest_pdf(sbi_path, user_id)
        print(f"[+] SBI engine natively extracted {len(sbi_txns)} document records securely.")
    else:
        print(f"[!] Target natively unstructured: {sbi_path} failed to locate.")
        
    print("\n" + "=" * 50)
    print("               DATA SEEDING COMPLETE               ")
    print("=" * 50)
    print(f"\nACTION REQUIRED:\nNavigate to 'pocket-cfo-frontend/app/page.js'\nUpdate the constant explicitly mapping bounds:")
    print(f'\n    const USER_ID = "{user_id}";\n')
    print("=" * 50)


if __name__ == "__main__":
    seed_demo_data()
