"""
Compliance engine services for Pocket CFO.

Implements hackathon-grade scaffolding for:
1) Account Aggregator (AA) FIU integration flow
2) MSME verification + Section 43B(h) payable aging checks
3) W-8BEN PDF + Form 15CA/15CB XML generation
4) Foreign SaaS OIDAR RCM detection + GST pre-flight checks
5) Compliance calendar reminders + DRL triggers
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from pocket_cfo_parser.db.mongo import (
    aa_consents_collection,
    aa_sessions_collection,
    compliance_calendar_collection,
    drl_requests_collection,
    foreign_remittances_collection,
    gst_preflight_collection,
    payables_collection,
    transactions_collection,
    vendors_collection,
)


# -----------------------------
# Phase 1: AA FIU flow
# -----------------------------

AA_STATUSES = {"PENDING", "ACTIVE", "REJECTED", "REVOKED", "EXPIRED", "PAUSED"}


def create_aa_consent(user_id: str, aa_handle: str, fi_types: list[str], from_date: str, to_date: str) -> dict:
    consent_id = f"consent-{uuid.uuid4().hex[:16]}"
    consent_handle = f"handle-{uuid.uuid4().hex[:12]}"
    redirect_url = f"https://aa.mock/consent/{consent_id}"
    doc = {
        "user_id": user_id,
        "consent_id": consent_id,
        "consent_handle": consent_handle,
        "aa_handle": aa_handle,
        "status": "PENDING",
        "fi_types": fi_types,
        "data_range": {"from": from_date, "to": to_date},
        "created_at": datetime.now().isoformat(),
    }
    aa_consents_collection.update_one({"consent_id": consent_id}, {"$set": doc}, upsert=True)
    aa_sessions_collection.update_one(
        {"consent_id": consent_id},
        {"$set": {"user_id": user_id, "consent_id": consent_id, "data_status": "PENDING", "fetch_attempts": 0}},
        upsert=True,
    )
    return {"consent_id": consent_id, "consent_handle": consent_handle, "redirect_url": redirect_url}


def update_aa_consent_status(consent_id: str, status: str, payload: dict | None = None) -> dict:
    status_norm = status.upper()
    if status_norm not in AA_STATUSES:
        status_norm = "PENDING"
    aa_consents_collection.update_one(
        {"consent_id": consent_id},
        {"$set": {"status": status_norm, "last_webhook": payload or {}, "updated_at": datetime.now().isoformat()}},
        upsert=True,
    )
    return {"consent_id": consent_id, "status": status_norm}


def mark_aa_data_ready(consent_id: str, session_id: str, payload: dict | None = None) -> dict:
    aa_sessions_collection.update_one(
        {"consent_id": consent_id},
        {
            "$set": {
                "consent_id": consent_id,
                "session_id": session_id,
                "data_status": "READY",
                "raw_meta": payload or {},
                "updated_at": datetime.now().isoformat(),
            }
        },
        upsert=True,
    )
    return {"consent_id": consent_id, "session_id": session_id, "data_status": "READY"}


def _hash_payload(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def fetch_aa_financial_data(consent_id: str, session_id: str, user_id: str) -> dict:
    # Hackathon flow: accepts already structured mock payload from webhook/fetch caller.
    # This function creates deterministic AA-native transactions for testing.
    seed_rows = [
        {"date": datetime.now().date().isoformat(), "amount": 13250.0, "type": "debit", "party": "AWS Singapore", "fi_type": "DEPOSIT"},
        {"date": datetime.now().date().isoformat(), "amount": 85400.0, "type": "credit", "party": "Customer NEFT", "fi_type": "DEPOSIT"},
        {"date": datetime.now().date().isoformat(), "amount": 15750.0, "type": "debit", "party": "Slack Billing", "fi_type": "DEPOSIT"},
    ]
    upserted = 0
    for row in seed_rows:
        payload_hash = _hash_payload(row)
        tx_doc = {
            "user_id": user_id,
            "amount": row["amount"],
            "type": row["type"],
            "party": row["party"],
            "date": row["date"],
            "source": "aa",
            "raw_text": f"AA:{row['party']}",
            "category": "General Business Expense" if row["type"] == "debit" else "Sales Income",
            "sub_category": "AA Import",
            "business_nature": "business",
            "confidence": 0.99,
            "aa": {
                "enabled": True,
                "consent_id": consent_id,
                "session_id": session_id,
                "fi_type": row["fi_type"],
                "verified": True,
                "fetched_at": datetime.now().isoformat(),
                "payload_hash": payload_hash,
                "raw": row,
            },
        }
        transactions_collection.update_one(
            {"user_id": user_id, "aa.payload_hash": payload_hash},
            {"$setOnInsert": tx_doc},
            upsert=True,
        )
        upserted += 1

    aa_sessions_collection.update_one(
        {"consent_id": consent_id},
        {"$set": {"data_status": "FETCHED", "fetched_at": datetime.now().isoformat()}, "$inc": {"fetch_attempts": 1}},
        upsert=True,
    )
    return {"consent_id": consent_id, "session_id": session_id, "upserted_transactions": upserted}


# -----------------------------
# Phase 2: MSME + 43B(h)
# -----------------------------

def verify_msme_vendor(user_id: str, vendor_name: str, pan: str, udyam_number: str | None = None) -> dict:
    # Placeholder for Decentro/Surepass integration response normalization.
    enterprise_type = "MICRO" if vendor_name.lower().startswith(("micro", "nano")) else "SMALL"
    record = {
        "user_id": user_id,
        "name": vendor_name,
        "pan": pan.upper(),
        "udyam_number": udyam_number or "",
        "has_written_agreement": False,
        "agreed_credit_days": None,
        "msme": {
            "verified": True,
            "enterprise_type": enterprise_type,
            "registration_date": "2021-04-01",
            "active_status": "ACTIVE",
            "source": "mock-msme-api",
            "fetched_at": datetime.now().isoformat(),
        },
    }
    vendors_collection.update_one({"user_id": user_id, "pan": pan.upper()}, {"$set": record}, upsert=True)
    return record


def create_payable_invoice(user_id: str, vendor_pan: str, invoice_number: str, invoice_date: str, amount: float) -> dict:
    vendor = vendors_collection.find_one({"user_id": user_id, "pan": vendor_pan.upper()})
    if not vendor:
        raise ValueError("Vendor not found. Verify MSME vendor first.")

    threshold_days = 45 if vendor.get("has_written_agreement") else 15
    msme_type = vendor.get("msme", {}).get("enterprise_type", "UNKNOWN")
    applicable = msme_type in {"MICRO", "SMALL"} and vendor.get("msme", {}).get("verified", False)

    inv_doc = {
        "user_id": user_id,
        "vendor_id": str(vendor.get("_id")),
        "vendor_pan": vendor_pan.upper(),
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "amount": amount,
        "amount_paid": 0.0,
        "status": "OPEN",
        "section_43bh": {
            "applicable": applicable,
            "threshold_days": threshold_days if applicable else None,
            "breached": False,
            "deduction_disallowance_flag": False,
        },
        "created_at": datetime.now().isoformat(),
    }
    payables_collection.update_one(
        {"user_id": user_id, "invoice_number": invoice_number, "vendor_pan": vendor_pan.upper()},
        {"$set": inv_doc},
        upsert=True,
    )
    return inv_doc


def run_43bh_aging(user_id: str) -> dict:
    now = datetime.now()
    cursor = payables_collection.find({"user_id": user_id, "status": {"$in": ["OPEN", "PART_PAID"]}})
    flagged = []
    for inv in cursor:
        sec = inv.get("section_43bh", {})
        if not sec.get("applicable"):
            continue
        threshold_days = int(sec.get("threshold_days") or 45)
        invoice_date = datetime.fromisoformat(inv["invoice_date"])
        age_days = (now - invoice_date).days
        breached = age_days > threshold_days
        if breached:
            payables_collection.update_one(
                {"_id": inv["_id"]},
                {"$set": {"section_43bh.breached": True, "section_43bh.deduction_disallowance_flag": True}},
            )
            flagged.append(
                {
                    "invoice_number": inv.get("invoice_number"),
                    "vendor_pan": inv.get("vendor_pan"),
                    "age_days": age_days,
                    "threshold_days": threshold_days,
                    "alert": "Potential deduction disallowance under Section 43B(h).",
                }
            )
    return {"user_id": user_id, "flagged_count": len(flagged), "alerts": flagged}


# -----------------------------
# Phase 3: W-8BEN + Form 15CA XML
# -----------------------------

@dataclass
class W8BENData:
    full_name: str
    registered_address: str
    pan: str
    country: str = "India"


def generate_w8ben_pdf(data: W8BENData, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename = f"w8ben_{data.pan}_{uuid.uuid4().hex[:8]}.pdf"
    full_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(full_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, 800, "W-8BEN (Individual) - Pocket CFO Draft")
    c.setFont("Helvetica", 11)
    c.drawString(40, 770, f"Line 1 - Name: {data.full_name}")
    c.drawString(40, 750, f"Line 2 - Country of citizenship: {data.country}")
    c.drawString(40, 730, f"Line 3 - Permanent residence address: {data.registered_address}")
    c.drawString(40, 710, f"Line 6a - Foreign TIN (PAN): {data.pan}")
    c.drawString(40, 680, "Generated for DTAA treaty claim support workflow.")
    c.showPage()
    c.save()
    return full_path


def generate_form_15ca_xml(remittance: dict[str, Any]) -> str:
    root = Element("Form15CA")
    remitter = SubElement(root, "Remitter")
    SubElement(remitter, "Name").text = str(remittance.get("remitter_name", ""))
    SubElement(remitter, "PAN").text = str(remittance.get("remitter_pan", ""))

    remittee = SubElement(root, "Remittee")
    SubElement(remittee, "Name").text = str(remittance.get("remittee_name", ""))
    SubElement(remittee, "Country").text = str(remittance.get("remittee_country", ""))

    payment = SubElement(root, "Payment")
    SubElement(payment, "AmountINR").text = str(remittance.get("amount_inr", 0))
    SubElement(payment, "PurposeCode").text = str(remittance.get("purpose_code", "P0802"))
    SubElement(payment, "DTAAApplicable").text = str(bool(remittance.get("dtaa_applicable", True))).lower()
    SubElement(payment, "Taxability").text = str(remittance.get("taxability", "TAXABLE"))
    SubElement(payment, "WithholdingRate").text = str(remittance.get("withholding_rate", 0))

    xml_bytes = tostring(root, encoding="utf-8")
    return xml_bytes.decode("utf-8")


def save_foreign_remittance(user_id: str, remittance: dict[str, Any]) -> dict:
    doc = {"user_id": user_id, **remittance, "created_at": datetime.now().isoformat()}
    foreign_remittances_collection.insert_one(doc)
    xml_payload = generate_form_15ca_xml(remittance) if float(remittance.get("amount_inr", 0)) > 500000 else ""
    return {"saved": True, "needs_form_15ca": float(remittance.get("amount_inr", 0)) > 500000, "xml": xml_payload}


# -----------------------------
# Phase 4: OIDAR + RCM + pre-flight
# -----------------------------

FOREIGN_SAAS_KEYS = {"aws", "slack", "github", "notion", "atlassian", "openai", "google cloud", "azure", "stripe"}


def detect_oidar_rcm(party: str, amount: float) -> dict:
    lower = (party or "").lower()
    matched = any(key in lower for key in FOREIGN_SAAS_KEYS)
    if not matched:
        return {"oidar_import": False, "rcm_applicable": False, "rcm_rate": 0.0, "igst_rcm_liability": 0.0}
    liability = round(float(amount) * 0.18, 2)
    return {
        "oidar_import": True,
        "rcm_applicable": True,
        "rcm_rate": 18.0,
        "igst_rcm_liability": liability,
        "classification": "Import of OIDAR services",
    }


def run_gst_preflight(gstr1_total_tax: float, gstr3b_total_tax: float, user_id: str) -> dict:
    diff = round(float(gstr1_total_tax) - float(gstr3b_total_tax), 2)
    blocked = abs(diff) > 1.0
    result = {
        "user_id": user_id,
        "gstr1_total_tax": float(gstr1_total_tax),
        "gstr3b_total_tax": float(gstr3b_total_tax),
        "difference": diff,
        "blocked": blocked,
        "message": "Submission blocked due to mismatch." if blocked else "Pre-flight passed.",
        "created_at": datetime.now().isoformat(),
    }
    gst_preflight_collection.insert_one(result)
    return result


# -----------------------------
# Phase 5: DRL + MCA scheduler
# -----------------------------

MCA_FORMS_BY_ENTITY = {
    "pvt_ltd": ["AOC-4", "MGT-7"],
    "llp": ["Form-11", "Form-8"],
    "opc": ["AOC-4", "MGT-7A"],
}


def schedule_compliance_calendar(user_id: str, entity_type: str, financial_year_end: str) -> dict:
    forms = MCA_FORMS_BY_ENTITY.get(entity_type.lower(), ["AOC-4", "MGT-7"])
    fy_end = datetime.fromisoformat(financial_year_end)
    due_base = fy_end + timedelta(days=180)
    reminders = []
    for form in forms:
        for offset in [30, 15, 3]:
            reminders.append(
                {
                    "form_code": form,
                    "due_date": due_base.date().isoformat(),
                    "reminder_date": (due_base - timedelta(days=offset)).date().isoformat(),
                    "offset_days": offset,
                }
            )
    doc = {
        "user_id": user_id,
        "entity_type": entity_type,
        "financial_year_end": financial_year_end,
        "reminders": reminders,
        "created_at": datetime.now().isoformat(),
    }
    compliance_calendar_collection.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
    return doc


def trigger_drl_if_missing_invoice(user_id: str, threshold_amount: float = 20000.0) -> dict:
    cursor = transactions_collection.find({"user_id": user_id, "type": "debit", "amount": {"$gte": threshold_amount}})
    triggered = []
    for txn in cursor:
        # invoice_file_id intentionally optional - triggers DRL when missing
        if txn.get("invoice_file_id"):
            continue
        req_id = f"drl-{uuid.uuid4().hex[:10]}"
        drl_doc = {
            "request_id": req_id,
            "user_id": user_id,
            "transaction_ref": str(txn.get("_id")),
            "party": txn.get("party", "Unknown"),
            "amount": txn.get("amount", 0.0),
            "status": "PENDING_UPLOAD",
            "upload_link": f"https://pocketcfo.local/upload/{req_id}",
            "created_at": datetime.now().isoformat(),
        }
        drl_requests_collection.update_one({"request_id": req_id}, {"$set": drl_doc}, upsert=True)
        triggered.append(drl_doc)
    return {"user_id": user_id, "drl_triggered_count": len(triggered), "requests": triggered}
