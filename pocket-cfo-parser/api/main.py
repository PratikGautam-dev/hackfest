"""
FastAPI Server Engine mapping AI extraction constraints and logic workflows 
dynamically into distinct operational HTTP intelligence endpoints securely.
"""
import os
import sys
# Automatically bind the project root to the Python path avoiding module import errors
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Imports from pocket_cfo_parser core logic
from pocket_cfo_parser.ingestion import ingest_sms, ingest_pdf
from pocket_cfo_parser.db.mongo import get_transactions_by_user
from pocket_cfo_parser.models.transaction import Transaction
from pocket_cfo_parser.agents.expense_agent import get_expense_summary
from pocket_cfo_parser.agents.profit_agent import get_profit_summary
from pocket_cfo_parser.agents.gst_agent import analyze_itc_opportunities

# Instantiate API architecture
app = FastAPI(
    title="Pocket CFO Agent API", 
    version="1.0.0"
)

# Safely inject permissive structural development bounds evaluating origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Expand origin scope globally (Will tightly bind down constraints explicitly later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Construct specific strict payload representations natively mapping validations explicitly
class SMSPayload(BaseModel):
    user_id: str
    text: str


@app.get("/health")
def health_check():
    """Simple healthcheck evaluating operational runtime uptime."""
    return {"status": "ok", "message": "Pocket CFO Agent is running"}


@app.post("/ingest/sms")
def ingest_sms_route(payload: SMSPayload):
    """
    Ingests fundamentally unstructured SMS structurally aggregating transaction flows 
    natively securely into databases implicitly resolving AI schemas.
    """
    txn = ingest_sms(payload.text, payload.user_id)
    if txn:
        return txn.to_dict()
    else:
        return {"status": "skipped", "reason": "non-transactional message"}


@app.post("/ingest/pdf")
async def ingest_pdf_route(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Uploads dynamic PDF structurally unpacking data matrices inherently 
    saving evaluated tables chronologically into DB reliably securely.
    """
    # Spawns isolated secure temporary container safely extracting native logic dimensions efficiently
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
        
    try:
        transactions = ingest_pdf(tmp_path, user_id)
        return {
            "transactions": [t.to_dict() for t in transactions],
            "count": len(transactions)
        }
    finally:
        # Dynamically guarantee native file deletion safely resolving logic bottlenecks reliably mathematically
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _fetch_user_transactions(user_id: str) -> list[Transaction]:
    """
    Helper dynamically unpacking primitive Mongo database representations 
    safely compiling robust active OOP models explicitly properly structurally.
    """
    raw_dicts = get_transactions_by_user(user_id)
    txns = []
    
    for r in raw_dicts:
        # Since 'id' is implicitly hashed by dependencies via __post_init__, 
        # reconstructing fields preserves boundaries cleanly automatically.
        txn = Transaction(
            amount=r.get("amount", 0.0),
            type=r.get("type", "debit"),
            party=r.get("party", "Unknown"),
            date=r.get("date"),
            source=r.get("source", "db"),
            category=r.get("category", "Uncategorized"),
            raw_text=r.get("raw_text", ""),
            confidence=r.get("confidence", 0.9)
        )
        # Note: We aren't preserving the exact _id mapping inside the newly constructed instance 
        # but for analytics processing dependencies, structural OOP parameters logically resolve appropriately.
        txns.append(txn)
        
    return txns


@app.get("/insights/{user_id}")
def insights_route(user_id: str):
    """
    Chronologically unpacks structured intelligence bounds dynamically providing 
    compound payloads aggregating metrics cleanly comprehensively inherently securely.
    """
    txns = _fetch_user_transactions(user_id)
    
    # Process distinct operational bounds dependencies logic securely
    expenses = get_expense_summary(txns)
    profits = get_profit_summary(txns)
    
    return {
        "expense_summary": expenses,
        "profit_summary": profits
    }


@app.get("/actions/{user_id}")
def actions_route(user_id: str):
    """
    Dynamically groups systemic diagnostic evaluations mapping triggers directly 
    translating numerical bounds trajectories into actionable operational dashboard components.
    """
    txns = _fetch_user_transactions(user_id)
    actions = []
    
    expenses = get_expense_summary(txns)
    profits = get_profit_summary(txns)
    itc_ops = analyze_itc_opportunities(txns)
    
    # 1. Red Cards (Critical Focus Required): Expense anomalies, Overall negative balances implicitly 
    for anomaly in expenses.get("anomalies", []):
        amt = anomaly.get("transaction", {}).get("amount", None)
        actions.append({
            "priority": "red",
            "title": "Unusual Spending Outlier Detected",
            "message": anomaly.get("anomaly_reason", "High mathematical variance explicitly defined bounds."),
            "amount": amt
        })
        
    net_profit = profits.get("net_profit", 0.0)
    if net_profit < 0:
        actions.append({
            "priority": "red",
            "title": "Deficit Bounds Alert",
            "message": "You're operating at a loss this period. Review your top expense categories to cut costs.",
            "amount": abs(net_profit)
        })
        
    # 2. Amber Cards (Warnings/Checks): Missed ITC structurally explicit bounds natively mapped
    missed_itc = itc_ops.get("missed_itc_count", 0)
    if missed_itc > 0:
        actions.append({
            "priority": "amber",
            "title": "Missed Input Tax Credit Diagnostics",
            "message": f"You have {missed_itc} transactions we couldn't classify confidently. Review them to unlock potential ITC claims.",
            "amount": None
        })
        
    low_confidence_count = sum(1 for t in txns if t.confidence <= 0.4)
    if low_confidence_count > 0:
        actions.append({
            "priority": "amber",
            "title": "Review Classification Thresholds natively",
            "message": f"AI couldn't classify {low_confidence_count} transactions with high confidence. Review and tag them manually.",
            "amount": None
        })
        
    # 3. Green Cards (Success/Goals): Profitable, High ITC dependencies structurally evaluated implicitly 
    claimable_itc = itc_ops.get("total_itc_claimable", 0.0)
    if claimable_itc > 0:
        actions.append({
            "priority": "green",
            "title": "Input Tax Credit Available",
            "message": f"You can claim ₹{claimable_itc:,.2f} in GST credits. File your ITC claims to improve cashflow.",
            "amount": claimable_itc
        })
        
    if net_profit > 0:
        actions.append({
            "priority": "green",
            "title": "Business is Profitable",
            "message": f"You made ₹{net_profit:,.2f} this period after expenses and GST recovery. Keep it up.",
            "amount": net_profit
        })

    return {
        "actions": actions,
        "user_id": user_id
    }


if __name__ == "__main__":
    # Boot the application securely mapping explicit local execution interfaces explicitly mathematically 
    uvicorn.run(app, host="0.0.0.0", port=8000)
