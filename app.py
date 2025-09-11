# app.py
# -----------------------------------------
# Flask backend for Donation Inventory
# SQLite persistence via SQLAlchemy
# CRUD endpoints:
#   GET    /api/donations
#   POST   /api/donations
#   PUT    /api/donations/<id>
#   DELETE /api/donations/<id>
# -----------------------------------------
from pathlib import Path
import os
from datetime import date, datetime
from typing import Dict, Any

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = Path(__file__).resolve().parent  # folder containing app.py
DB_PATH = BASE_DIR / "donations.db"
app = Flask(__name__)

# SQLite database file
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Allow all origins for simplicity (OK for local dev)
CORS(app)

db = SQLAlchemy(app)

# ------------------ Models ------------------

class Donation(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String, nullable=False)
    donation_type = db.Column(db.String, nullable=False)  # money, food, clothing, etc.
    quantity_or_amount = db.Column(db.Integer, nullable=False)  # store as integer
    date = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        # Serialize to JSON-friendly dict
        return {
            "id": self.id,
            "donor_name": self.donor_name,
            "donation_type": self.donation_type,
            "quantity_or_amount": self.quantity_or_amount,
            # Return ISO string (yyyy-mm-dd)
            "date": self.date.isoformat(),
        }


# Create tables if they don't exist yet
with app.app_context():
    db.create_all()

# ---------------- Helpers/validation ----------------

def parse_iso_date(value: str) -> date:
    """
    Accepts 'YYYY-MM-DD' (from <input type="date">) or full ISO strings.
    Returns a Python date object or aborts 400 on bad format.
    """
    if not isinstance(value, str):
        abort(400, description="date must be a string in ISO format (YYYY-MM-DD)")
    try:
        # Try just date first
        return datetime.fromisoformat(value).date()
    except ValueError:
        abort(400, description="Invalid date format; expected ISO (YYYY-MM-DD)")

def validate_payload(payload: dict, partial: bool = False) -> dict:
    """
    Validate request JSON for create/update.
    - partial=True: allow missing fields (PUT); only validate provided ones.
    - partial=False: all fields required (POST).
    """
    allowed_types = {"money", "food", "clothing", "other"}

    # Helper to fetch and validate fields
    def get_str(key, required=not partial):
        v = payload.get(key)
        if v is None:
            if required:
                abort(400, description=f"Missing required field: {key}")
            return None
        if not isinstance(v, str) or not v.strip():
            abort(400, description=f"{key} must be a non-empty string")
        return v.strip()

    def get_int(key, required=not partial):
        v = payload.get(key)
        if v is None:
            if required:
                abort(400, description=f"Missing required field: {key}")
            return None
        if not isinstance(v, int) or v < 1:
            abort(400, description=f"{key} must be a positive integer")
        return v

    out = {}

    donor_name = get_str("donor_name")
    if donor_name is not None:
        out["donor_name"] = donor_name

    donation_type = get_str("donation_type")
    if donation_type is not None:
        if donation_type not in allowed_types:
            abort(400, description=f"donation_type must be one of {sorted(allowed_types)}")
        out["donation_type"] = donation_type

    qty = get_int("quantity_or_amount")
    if qty is not None:
        out["quantity_or_amount"] = qty

    date_str = payload.get("date")
    if date_str is None and not partial:
        abort(400, description="Missing required field: date")
    if date_str is not None:
        out["date"] = parse_iso_date(date_str)

    return out

# ------------------ Routes ------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/api/donations", methods=["GET"])
def list_donations():
    rows = Donation.query.order_by(Donation.id.desc()).all()
    return jsonify([r.to_dict() for r in rows])

@app.route("/api/donations", methods=["POST"])
def create_donation():
    if not request.is_json:
        abort(400, description="Request must be application/json")
    payload = request.get_json()
    data = validate_payload(payload, partial=False)

    row = Donation(
        donor_name=data["donor_name"],
        donation_type=data["donation_type"],
        quantity_or_amount=data["quantity_or_amount"],
        date=data["date"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.session.add(row)
    db.session.commit()

    return jsonify(row.to_dict()), 201

@app.route("/api/donations/<int:donation_id>", methods=["PUT"])
def update_donation(donation_id: int):
    if not request.is_json:
        abort(400, description="Request must be application/json")
    payload = request.get_json()
    data = validate_payload(payload, partial=True)

    row = Donation.query.get(donation_id)
    if not row:
        abort(404, description="Donation not found")

    # Apply only provided fields
    if "donor_name" in data: row.donor_name = data["donor_name"]
    if "donation_type" in data: row.donation_type = data["donation_type"]
    if "quantity_or_amount" in data: row.quantity_or_amount = data["quantity_or_amount"]
    if "date" in data: row.date = data["date"]

    row.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(row.to_dict())

@app.route("/api/donations/<int:donation_id>", methods=["DELETE"])
def delete_donation(donation_id: int):
    row = Donation.query.get(donation_id)
    if not row:
        abort(404, description="Donation not found")
    db.session.delete(row)
    db.session.commit()
    return ("", 204)  # No Content
