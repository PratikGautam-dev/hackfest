"""
Sample SMS messages for testing the pocket-cfo-parser SMS parser.
Contains 15 realistic Indian bank UPI SMS texts covering variations in banks,
transaction formats, failures, promotional texts, and OTPs.
"""

SAMPLE_SMS = [
    # 1. HDFC Bank - UPI Debit
    "UPDATE: Rs. 250.00 has been debited from your HDFC Bank A/c xx1234 on 14-Apr-26 to SWIGGY. UPI Ref No. 610543679802.",
    
    # 2. HDFC Bank - UPI Credit
    "Rs 5,000.00 deposited to your HDFC Bank A/c xx1234. Info: UPI-Rahul Kumar-610543987102. Available Bal: Rs. 24,500.25.",
    
    # 3. SBI - UPI Debit (with multi-word party name and paisa amount)
    "Dear SBI User, your A/c XXXXXX5678-debited by Rs1250.50 on 14Apr26 trf to Raj Medical Store Ref No 610489000123. If not done by u forward this SMS to 9223008333.",
    
    # 4. SBI - UPI Credit
    "Dear Customer, A/c XXXXXX5678 is credited by Rs 1500.00 on 14-Apr-26. UPI Ref: 610512398450 (By: Neha Sharma). Bal: Rs 15,200.00",
    
    # 5. ICICI Bank - UPI Debit
    "Dear Customer, Acct XX8901 is debited for Rs 850.00 on 14-04-2026 12:45:00 and credited to VPA zomato@icici. UPI Ref: 609812445566.",
    
    # 6. ICICI Bank - UPI Credit
    "Your A/c no. XX8901 is credited with Rs. 12,000.00 on 13-04-2026 by UPI. UPI Ref. No. 608823129841. Info: Rent Payment.",
    
    # 7. Axis Bank - UPI Debit
    "INR 3,400.00 withdrawn from A/c no. XX4555 on 14-04-26. Info: UPI/610599882200/Amazon Pay/axisbank/UPI. Available Balance is INR 42,100.00.",
    
    # 8. Kotak Bank - UPI Credit
    "Rs. 25000 is credited to your Kotak Bank A/c XX3344 on 12-04-26 from UPI. Ref No: 610234771199. Bal: Rs. 85,000.",
    
    # 9. Failed/Declined transaction (Should be ignored by parser)
    "DECLINED: Your UPI payment of Rs. 450.00 to Uber India via HDFC Bank A/c xx1234 failed due to insufficient funds. UPI Ref No. 610545672210.",
    
    # 10. Non-transaction (OTP) - (Should be ignored by parser)
    "Your OTP to login to HDFC Bank MobileBanking is 845213. Do not share this with anyone.",
    
    # 11. Non-transaction (Promotional) - (Should be ignored by parser)
    "Exclusive Offer! Apply for lifetime free SBI Credit Card today and get an Amazon voucher worth Rs. 500. Click https://sbi.co.in/c to apply. T&C Apply.",
    
    # 12. HDFC Bank - UPI Debit (Alternative format)
    "Money Transfer: Rs 1,100.00 debited from A/c xx1234 on 14-04-2026 to VPA airtel@ybl. Ref: 610543229988.",
    
    # 13. SBI - UPI Debit (Alternative format)
    "Dear SBI User, your A/c XXXXXX5678-debited by Rs 150.00 on 13Apr26 trf to Reliance Fresh Ref No 609211223344.",
    
    # 14. ICICI Bank - UPI Debit (Alternative format)
    "Txn of INR 550.00 done on your ICICI Bank A/c XX8901 on 14-Apr-26 using UPI. Sent to Jio Prepaid. UPI Refno: 610555443322.",
    
    # 15. Kotak Bank - UPI Debit
    "You have sent Rs. 99.00 to Netflix via Kotak A/c XX3344. UPI Ref: 610511442288. Bal: Rs. 84,901.00."
]
