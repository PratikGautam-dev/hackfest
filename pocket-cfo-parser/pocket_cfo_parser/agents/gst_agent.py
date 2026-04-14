"""
GST Agent
Determines GST classifications and calculates Input Tax Credit (ITC) eligibility via deterministic rules,
with an AI fallback mechanism powered by Google Gemini.
"""

import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from pocket_cfo_parser.models.transaction import Transaction

# Initialize env variables globally
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Predefined rules map lowercase keywords to structured GST parameters
# Expanding to 50+ explicit rule sets
GST_RULES = {
    # Food & Grocery
    "blinkit": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    "zepto": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    "bigbasket": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    "grofers": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    "dmart": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    "reliance fresh": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    "more supermarket": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    "spencers": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food & Grocery"},
    
    # Pharma & Health
    "apollo": {"gst_rate": 12.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Pharma & Health"},
    "netmeds": {"gst_rate": 12.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Pharma & Health"},
    "pharmeasy": {"gst_rate": 12.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Pharma & Health"},
    "medplus": {"gst_rate": 12.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Pharma & Health"},
    "1mg": {"gst_rate": 12.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Pharma & Health"},
    "thyrocare": {"gst_rate": 12.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Pharma & Health"},
    "lenskart": {"gst_rate": 12.0, "hsn_sac": "9993", "itc_eligible": False, "category": "Pharma & Health"},
    
    # Ride & Logistics
    "rapido": {"gst_rate": 5.0, "hsn_sac": "9964", "itc_eligible": False, "category": "Ride & Logistics"},
    "dunzo": {"gst_rate": 18.0, "hsn_sac": "9967", "itc_eligible": True, "category": "Ride & Logistics"},
    "porter": {"gst_rate": 18.0, "hsn_sac": "9967", "itc_eligible": True, "category": "Ride & Logistics"},
    "delhivery": {"gst_rate": 18.0, "hsn_sac": "9967", "itc_eligible": True, "category": "Ride & Logistics"},
    "bluedart": {"gst_rate": 18.0, "hsn_sac": "9967", "itc_eligible": True, "category": "Ride & Logistics"},
    "dtdc": {"gst_rate": 18.0, "hsn_sac": "9967", "itc_eligible": True, "category": "Ride & Logistics"},
    "ecom express": {"gst_rate": 18.0, "hsn_sac": "9967", "itc_eligible": True, "category": "Ride & Logistics"},
    
    # Fashion & Lifestyle
    "myntra": {"gst_rate": 12.0, "hsn_sac": "9961", "itc_eligible": True, "category": "Fashion & Lifestyle"},
    "nykaa": {"gst_rate": 12.0, "hsn_sac": "9961", "itc_eligible": True, "category": "Fashion & Lifestyle"},
    "ajio": {"gst_rate": 12.0, "hsn_sac": "9961", "itc_eligible": True, "category": "Fashion & Lifestyle"},
    "meesho": {"gst_rate": 12.0, "hsn_sac": "9961", "itc_eligible": True, "category": "Fashion & Lifestyle"},
    "bewakoof": {"gst_rate": 12.0, "hsn_sac": "9961", "itc_eligible": True, "category": "Fashion & Lifestyle"},
    
    # Payments & Fintech
    "paytm": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Payments & Fintech"},
    "phonepe": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Payments & Fintech"},
    "gpay": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Payments & Fintech"},
    "razorpay": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Payments & Fintech"},
    "cashfree": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Payments & Fintech"},
    
    # Food chains
    "mcdonald": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food Chains"},
    "dominos": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food Chains"},
    "pizza hut": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food Chains"},
    "kfc": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food Chains"},
    "subway": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food Chains"},
    "starbucks": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food Chains"},
    "cafe coffee day": {"gst_rate": 5.0, "hsn_sac": "9963", "itc_eligible": False, "category": "Food Chains"},
    
    # Telecom & Cloud
    "google": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": True, "category": "Telecom & Cloud"},
    "microsoft": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": True, "category": "Telecom & Cloud"},
    "aws": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": True, "category": "Telecom & Cloud"},
    "digitalocean": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": True, "category": "Telecom & Cloud"},
    "godaddy": {"gst_rate": 18.0, "hsn_sac": "9984", "itc_eligible": True, "category": "Telecom & Cloud"},
    
    # Education
    "udemy": {"gst_rate": 18.0, "hsn_sac": "9992", "itc_eligible": False, "category": "Education"},
    "coursera": {"gst_rate": 18.0, "hsn_sac": "9992", "itc_eligible": False, "category": "Education"},
    "unacademy": {"gst_rate": 18.0, "hsn_sac": "9992", "itc_eligible": False, "category": "Education"},
    "byju": {"gst_rate": 18.0, "hsn_sac": "9992", "itc_eligible": False, "category": "Education"},
    "vedantu": {"gst_rate": 18.0, "hsn_sac": "9992", "itc_eligible": False, "category": "Education"},
    
    # Fuel
    "hpcl": {"gst_rate": 0.0, "hsn_sac": "EXEMPT", "itc_eligible": False, "category": "Fuel"},
    "bpcl": {"gst_rate": 0.0, "hsn_sac": "EXEMPT", "itc_eligible": False, "category": "Fuel"},
    "iocl": {"gst_rate": 0.0, "hsn_sac": "EXEMPT", "itc_eligible": False, "category": "Fuel"},
    "petrol": {"gst_rate": 0.0, "hsn_sac": "EXEMPT", "itc_eligible": False, "category": "Fuel"},
    "diesel": {"gst_rate": 0.0, "hsn_sac": "EXEMPT", "itc_eligible": False, "category": "Fuel"},
    
    # Banking fees
    "processing fee": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Banking Fees"},
    "bank charges": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Banking Fees"},
    "emi": {"gst_rate": 18.0, "hsn_sac": "9971", "itc_eligible": True, "category": "Banking Fees"},

    # Legacy predefined constraints 
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


def _classify_with_gemini(party: str, amount: float) -> dict:
    """
    Fallback agent powered by Google Gemini dynamically categorizing
    ambiguous merchants into standard internal taxonomies.
    """
    fallback_payload = {
        "hsn_sac": "UNKNOWN",
        "gst_rate": 18.0,
        "itc_eligible": False,
        "category": "Uncategorized",
        "matched_rule": None,
        "confidence": 0.4
    }
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not party or party.lower() == "unknown":
        return fallback_payload

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Classify the merchant "{party}" (Transaction amount: {amount}) into one of these categories:
        Food & Beverage, Transport, Utilities, Healthcare, Retail, Software & Subscriptions, 
        Financial Services, Education, Fuel, Payroll, Uncategorized.
        
        Respond in JSON only with these fields exactly:
        - category: string
        - gst_rate: float (must be one of 0, 5, 12, 18, 28)
        - itc_eligible: boolean (true if typical businesses can claim ITC for this, otherwise false)
        - hsn_sac: string (best guess, e.g. '9984' or 'EXEMPT')
        
        Output only the pure JSON text without any markdown wrapper blocks.
        """
        
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        text = response.text.strip()
        
        # Strip potential markdown formatting if model didn't implicitly obey
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        
        return {
            "hsn_sac": result.get("hsn_sac", "UNKNOWN"),
            "gst_rate": float(result.get("gst_rate", 18.0)),
            "itc_eligible": bool(result.get("itc_eligible", False)),
            "category": result.get("category", "Uncategorized"),
            "matched_rule": "gemini",
            "confidence": 0.7
        }
    except Exception as e:
        logger.error(f"Gemini Inference Engine failure: {e}")
        return fallback_payload


def classify_transaction(transaction: Transaction) -> dict:
    """
    Analyzes a transaction and determines applicable GST parameters 
    based on known party-matching rules or Gemini LLM deduction context.
    Calculates back-dated GST and resolves explicit ITC claim bounds.
    """
    party_lower = transaction.party.lower() if transaction.party else ""
    
    # Scan the rules engine against the party name string mapping priority match
    for key, rule in GST_RULES.items():
        if key in party_lower:
            gst_rate = rule["gst_rate"]
            itc_eligible = rule["itc_eligible"]
            
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
            
    # Proceed to intelligence fallback 
    gemini_result = _classify_with_gemini(transaction.party, transaction.amount)
    
    # Destructure parameters for ITC calculation operations 
    gst_rate = gemini_result["gst_rate"]
    itc_eligible = gemini_result["itc_eligible"]
    
    gst_amount = transaction.amount * gst_rate / (100.0 + gst_rate)
    itc_amount = gst_amount if itc_eligible else 0.0
    
    gemini_result["gst_amount"] = round(gst_amount, 2)
    gemini_result["itc_amount"] = round(itc_amount, 2)
    
    return gemini_result


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
