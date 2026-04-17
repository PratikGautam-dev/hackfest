"""
FastAPI Server Engine mapping AI extraction constraints and logic workflows 
dynamically into distinct operational HTTP intelligence endpoints securely.
"""
import os
import sys
from datetime import datetime
# Automatically bind the project root to the Python path avoiding module import errors
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Imports from pocket_cfo_parser core logic
from pocket_cfo_parser.ingestion import ingest_sms, ingest_pdf
from pocket_cfo_parser.db.mongo import get_transactions_by_user, save_user
from pocket_cfo_parser.models.transaction import Transaction
from pocket_cfo_parser.agents.expense_agent import get_expense_summary
from pocket_cfo_parser.agents.profit_agent_v2 import get_profit_summary as get_profit_summary_v2
from pocket_cfo_parser.agents.gst_agent import analyze_itc_opportunities
from pocket_cfo_parser.agents.tax_savings_agent import get_tax_insights
from pocket_cfo_parser.agents.gstr_report_agent import generate_gst_compliance_report
from pocket_cfo_parser.agents.bookkeeping_agent import get_bookkeeping_summary
from pocket_cfo_parser.agents.financial_statements_agent import get_financial_statements
from pocket_cfo_parser.agents.income_tax_agent import get_income_tax_summary
from pocket_cfo_parser.agents.reconciliation_agent import get_reconciliation_report
from pocket_cfo_parser.agents.audit_agent import get_audit_report

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

class UserCreatePayload(BaseModel):
    name: str
    phone: str
    business_name: str

@app.post("/users/create")
def create_user_route(payload: UserCreatePayload):
    """Dynamically structurally bounds OOP mappings routing native MongoDB user creation."""
    user_id = save_user(payload.name, payload.phone, payload.business_name)
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return {"success": True, "backend_user_id": user_id}

@app.get("/users/{user_id}/profile")
def user_profile_route(user_id: str):
    """Evaluate topological boundaries aggregating transactional mapping counts securely natively."""
    txns = get_transactions_by_user(user_id)
    return {"user_id": user_id, "transaction_count": len(txns)}

@app.get("/transactions/{user_id}")
def user_transactions_route(user_id: str):
    """Exposes raw sequential MongoDB extractions cleanly bounded intrinsically iteratively."""
    txns = _fetch_user_transactions(user_id)
    sorted_txns = sorted(txns, key=lambda x: x.date, reverse=True)[:100]
    return {"transactions": [t.to_dict() for t in sorted_txns], "user_id": user_id}


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
        raw_date = r.get("date")
        if isinstance(raw_date, str):
            try:
                txn_date = datetime.fromisoformat(raw_date)
            except ValueError:
                txn_date = datetime.now()
        elif isinstance(raw_date, datetime):
            txn_date = raw_date
        else:
            txn_date = datetime.now()

        txn = Transaction(
            amount=r.get("amount", 0.0),
            type=r.get("type", "debit"),
            party=r.get("party", "Unknown"),
            date=txn_date,
            source=r.get("source", "sms"),
            category=r.get("category", "Uncategorized"),
            sub_category=r.get("sub_category", "Uncategorized"),
            business_nature=r.get("business_nature", "business"),
            gst_rate=r.get("gst_rate", 0.0),
            itc_eligible=r.get("itc_eligible", False),
            hsn_sac=r.get("hsn_sac", "UNKNOWN"),
            gst_amount=r.get("gst_amount", 0.0),
            itc_amount=r.get("itc_amount", 0.0),
            matched_rule=r.get("matched_rule", "none"),
            raw_text=r.get("raw_text", ""),
            confidence=r.get("confidence", 0.9)
        )
        txns.append(txn)
        
    return txns


@app.get("/insights/{user_id}")
def insights_route(user_id: str):
    """
    High-level financial insights for dashboard.
    Quick overview of profit, expenses, and tax opportunities.
    """
    txns = _fetch_user_transactions(user_id)
    
    profit_data = get_profit_summary_v2(txns)
    expense_data = get_expense_summary(txns)
    tax_data = get_tax_insights(txns)
    
    return {
        "user_id": user_id,
        "financial_overview": {
            "period": "Last 30 days",
            "net_profit": profit_data["overall"]["net_profit"],
            "total_revenue": profit_data["overall"]["total_revenue"],
            "total_expenses": profit_data["overall"]["total_expenses"],
            "profit_margin_percent": profit_data["overall"]["profit_margin_percent"],
            "transactions_processed": profit_data["overall"]["transaction_count"]
        },
        "top_expense_categories": {
            cat: data["total_expenses"]
            for cat, data in sorted(
                expense_data.get("by_category", {}).items(),
                key=lambda x: x[1]["total_spent"],
                reverse=True
            )[:5]
        },
        "tax_opportunities": {
            "potential_monthly_savings": tax_data["summary"]["potential_savings_per_month"],
            "quick_wins": tax_data["quick_wins"],
            "total_action_items": tax_data["summary"]["total_action_items"]
        },
        "generated_at": datetime.now().isoformat()
    }


@app.get("/expenses/{user_id}")
def expenses_route(user_id: str):
    txns = _fetch_user_transactions(user_id)
    return get_expense_summary(txns)


@app.get("/profit/{user_id}")
def profit_route(user_id: str):
    txns = _fetch_user_transactions(user_id)
    return get_profit_summary_v2(txns)


@app.get("/tax-savings/{user_id}")
def tax_savings_route(user_id: str):
    """
    Tax optimization strategies and potential savings.
    Recommends ways to maximize ITC, optimize expenses, and reduce tax burden.
    """
    txns = _fetch_user_transactions(user_id)
    insights = get_tax_insights(txns)
    return {
        "user_id": user_id,
        "tax_insights": insights,
        "generated_at": datetime.now().isoformat()
    }


@app.get("/bookkeeping/{user_id}")
def bookkeeping_route(user_id: str):
    """
    Bookkeeping summary for ledger review.
    Includes cashbook entries, category counts, GST and ITC totals, and bookkeeping remarks.
    """
    txns = _fetch_user_transactions(user_id)
    summary = get_bookkeeping_summary(txns)
    return {
        "user_id": user_id,
        "bookkeeping_summary": summary,
        "generated_at": datetime.now().isoformat()
    }


@app.get("/gst-report/{user_id}")
def gst_report_route(user_id: str):
    """
    Complete GST compliance report package:
    - GSTR-1 draft (outward supplies)
    - GSTR-3B draft (monthly return)
    - ITC summary
    - Filing checklist
    """
    txns = _fetch_user_transactions(user_id)
    report = generate_gst_compliance_report(txns)
    return {
        "user_id": user_id,
        "report": report
    }


@app.get("/financial-statements/{user_id}")
def financial_statements_route(user_id: str):
    """
    Generate core financial statements for CA review:
    - Profit & Loss statement
    - Simplified Balance Sheet
    - Cash Flow statement
    """
    txns = _fetch_user_transactions(user_id)
    statements = get_financial_statements(txns)
    return {
        "user_id": user_id,
        "financial_statements": statements,
        "generated_at": datetime.now().isoformat()
    }


@app.get("/income-tax/{user_id}")
def income_tax_route(user_id: str):
    """
    Estimate income tax liability and common deductions based on transaction history.
    """
    txns = _fetch_user_transactions(user_id)
    summary = get_income_tax_summary(txns)
    return {
        "user_id": user_id,
        "income_tax_summary": summary,
        "generated_at": datetime.now().isoformat()
    }


@app.get("/reconciliation/{user_id}")
def reconciliation_route(user_id: str):
    """
    Run a reconciliation assessment to detect duplicates, gaps, and matching issues.
    """
    txns = _fetch_user_transactions(user_id)
    report = get_reconciliation_report(txns)
    return {
        "user_id": user_id,
        "reconciliation_report": report,
        "generated_at": datetime.now().isoformat()
    }


@app.get("/audit/{user_id}")
def audit_route(user_id: str):
    """
    Audit and validate transaction accuracy, GST consistency, and suspicious patterns.
    """
    txns = _fetch_user_transactions(user_id)
    report = get_audit_report(txns)
    return {
        "user_id": user_id,
        "audit_report": report,
        "generated_at": datetime.now().isoformat()
    }


@app.get("/ca-summary/{user_id}")
def ca_summary_route(user_id: str):
    """
    Complete CA-level financial summary for the user.
    Combines: Profit, Expenses, Tax Savings, and GST Compliance.
    """
    txns = _fetch_user_transactions(user_id)
    
    profit_data = get_profit_summary_v2(txns)
    expense_data = get_expense_summary(txns)
    tax_data = get_tax_insights(txns)
    gst_data = generate_gst_compliance_report(txns)
    financial_statements = get_financial_statements(txns)
    income_tax = get_income_tax_summary(txns)
    reconciliation = get_reconciliation_report(txns)
    audit = get_audit_report(txns)
    
    return {
        "user_id": user_id,
        "summary": {
            "net_profit": profit_data["overall"]["net_profit"],
            "total_revenue": profit_data["overall"]["total_revenue"],
            "total_expenses": profit_data["overall"]["total_expenses"],
            "profit_margin": profit_data["overall"]["profit_margin_percent"],
            "potential_monthly_savings": tax_data["summary"]["potential_savings_per_month"],
            "claimable_itc": tax_data["summary"]["potential_savings_per_month"],
            "gst_payable": gst_data["report"]["gstr_3b"]["section_3_net_payable"]["net_gst_payable"],
            "refund_available": gst_data["report"]["gstr_3b"]["section_3_net_payable"]["net_refund_available"],
            "taxable_income": income_tax["taxable_income_summary"]["taxable_income"],
            "reconciliation_issues": reconciliation["issues"]["summary"],
            "audit_flags": audit["summary"]
        },
        "detailed_breakdown": {
            "profit": profit_data,
            "expenses": expense_data,
            "tax_opportunities": tax_data,
            "gst_compliance": gst_data,
            "financial_statements": financial_statements,
            "income_tax": income_tax,
            "reconciliation": reconciliation,
            "audit": audit
        },
        "action_items": tax_data["summary"]["high_priority_items"],
        "generated_at": datetime.now().isoformat()
    }


@app.get("/gst/{user_id}")
def gst_route(user_id: str):
    txns = _fetch_user_transactions(user_id)
    return analyze_itc_opportunities(txns)


@app.get("/actions/{user_id}")
def actions_route(user_id: str):
    """
    Dynamically groups systemic diagnostic evaluations mapping triggers directly 
    translating numerical bounds trajectories into actionable operational dashboard components.
    """
    txns = _fetch_user_transactions(user_id)
    actions = []
    
    expenses = get_expense_summary(txns)
    profits = get_profit_summary_v2(txns)
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
        
    net_profit = profits.get("overall", {}).get("net_profit", 0.0)
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
