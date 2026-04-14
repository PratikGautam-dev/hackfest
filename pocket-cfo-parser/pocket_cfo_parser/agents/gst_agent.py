"""
GST Agent
Determines GST classifications and calculates Input Tax Credit (ITC) eligibility via deterministic rules.
"""

from pocket_cfo_parser.models.transaction import Transaction

# GST Classification Rules Engine
# Predefined rules map lowercase keywords to structured GST parameters
GST_RULES = {
    "swiggy": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Beverage"},
    "zomato": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Beverage"},
    "amazon": {"gst_rate": 18.0, "hsn_sac": "9961", "itc_eligible": True, "category": "Retail & E-commerce"},
    "flipkart": {"gst_rate": 18.0, "hsn_sac": "9961", "itc_eligible": True, "category": "Retail & E-commerce"},
    "uber": {"gst_rate": 5.0, "hsn_sac": "9964", "itc_eligible": False, "category": "Transport"},
    "ola": {"gst_rate": 5.0, "hsn_sac": "9964", "itc_eligible": False, "category": "Transport"},
    "airtel": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": True, "category": "Telecommunications"},
    "jio": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": True, "category": "Telecommunications"},
    "electricity": {"gst_rate": 0.0, "hsn_sac": "EXEMPT", "itc_eligible": False, "category": "Utilities"},
    "rent": {"gst_rate": 18.0, "hsn_sac": "9972", "itc_eligible": True, "category": "Rent & Real Estate"},
    "salary": {"gst_rate": 0.0, "hsn_sac": "EXEMPT", "itc_eligible": False, "category": "Payroll"},
    "medical": {"gst_rate": 0.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Healthcare"},
    "hotel": {"gst_rate": 12.0, "hsn_sac": "9963", "itc_eligible": True, "category": "Accommodation"},
    "airline": {"gst_rate": 5.0, "hsn_sac": "9964", "itc_eligible": True, "category": "Airlines"},
    "railway": {"gst_rate": 5.0, "hsn_sac": "9964", "itc_eligible": True, "category": "Railways"},
    "insurance": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Financial Services"},
    "mutual fund": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": False, "category": "Investments"},
    "netflix": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": False, "category": "Software & Subscriptions"},
    "software": {"gst_rate": 18.0, "hsn_sac": "9973", "itc_eligible": True, "category": "Software & Subscriptions"},
    "office supplies": {"gst_rate": 18.0, "hsn_sac": "9983", "itc_eligible": True, "category": "Office Expenses"}
}


def classify_transaction(transaction: Transaction) -> dict:
    """
    Analyzes a transaction and determines applicable GST parameters based on known party-matching rules.
    Calculates back-dated GST and resolves explicit ITC boundaries via deterministic keywords constraints.
    """
    party_lower = transaction.party.lower() if transaction.party else ""
    
    # Scan the rules engine against the party name string mapping
    for key, rule in GST_RULES.items():
        if key in party_lower:
            gst_rate = rule["gst_rate"]
            itc_eligible = rule["itc_eligible"]
            
            # Back-calculate the GST implicitly contained across transaction sum instances
            # Mathematical algorithm: GST = Amount * Rate / (100 + Rate)
            gst_amount = transaction.amount * gst_rate / (100.0 + gst_rate)
            itc_amount = gst_amount if itc_eligible else 0.0
            
            return {
                "hsn_sac": rule["hsn_sac"],
                "gst_rate": gst_rate,
                "itc_eligible": itc_eligible,
                "category": rule["category"],
                "gst_amount": round(gst_amount, 2),
                "itc_amount": round(itc_amount, 2),
                "matched_rule": key,
                "confidence": 0.9
            }
            
    # Fallback to the Uncategorized default parameter configurations
    gst_rate = 18.0
    gst_amount = transaction.amount * gst_rate / (100.0 + gst_rate)
    return {
        "hsn_sac": "UNKNOWN",
        "gst_rate": gst_rate,
        "itc_eligible": False,
        "category": "Uncategorized",
        "gst_amount": round(gst_amount, 2),
        "itc_amount": 0.0,
        "matched_rule": None,
        "confidence": 0.4
    }

def analyze_itc_opportunities(transactions: list[Transaction]) -> dict:
    """
    Scans a chronological series of structured Transactions to calculate
    and formulate aggregated claimable Input Tax Credit intelligence.
    """
    total_itc = 0.0
    itc_transactions = []
    missed_itc_count = 0
    
    for txn in transactions:
        # ITC evaluations strictly require debits (business expenses structure mapping)
        if txn.type != "debit":
            continue
            
        classification = classify_transaction(txn)
        
        # Low confidence + Uncategorized indicates missed opportunistic parsing
        if classification["confidence"] <= 0.4 and classification["category"] == "Uncategorized":
            missed_itc_count += 1
            
        # Compile viable deductions
        if classification["itc_amount"] > 0:
            total_itc += classification["itc_amount"]
            
            # We map into dictionaries and attach our structured internal evaluations
            decorated_txn = txn.to_dict()
            decorated_txn["gst_classification"] = classification
            itc_transactions.append(decorated_txn)
            
    total_itc = round(total_itc, 2)
    
    # Formulate user-friendly English diagnostic metric strings
    summary = f"You can claim ₹{total_itc:,.2f} in Input Tax Credit across {len(itc_transactions)} transactions."
    
    return {
        "total_itc_claimable": total_itc,
        "itc_transactions": itc_transactions,
        "missed_itc_count": missed_itc_count,
        "summary": summary
    }
