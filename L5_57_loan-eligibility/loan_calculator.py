"""Loan eligibility and repayment calculations for a small loan book."""

import smtplib
from http.client import HTTPSConnection
import json
import os
import secrets
import ssl
from datetime import datetime
from email.message import EmailMessage
from urllib.parse import quote, urlparse

MAX_FOIR = 0.5
applications = {}


def calculate_emi(principal, annual_rate, years):
    """Return the fixed monthly payment for an annual decimal interest rate."""
    if principal < 0 or annual_rate < 0 or years <= 0:
        raise ValueError(
            "principal and rate must be nonnegative; years must be positive"
        )
    months = years * 12
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / months
    rate_factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * rate_factor / (rate_factor - 1)


def check_eligibility(age, income, credit_score, existing_emi, loan_type):
    """Check basic age, affordability, credit, and supported-product rules."""
    supported_types = {"home", "car", "personal"}
    if age < 21 or age > 60 or income <= 0 or existing_emi < 0:
        return False
    if (
        credit_score < 300
        or credit_score > 900
        or loan_type not in supported_types
    ):
        return False
    if existing_emi / income > MAX_FOIR:
        return False
    return True


def max_loan_amount(income, existing_emi, annual_rate, years):
    """Return the principal affordable at the remaining monthly FOIR amount."""
    if income <= 0 or existing_emi < 0:
        raise ValueError(
            "income must be positive and existing EMI nonnegative"
        )
    monthly_payment = max(0, income * MAX_FOIR - existing_emi)
    months = years * 12
    if years <= 0 or annual_rate < 0:
        raise ValueError("years must be positive and annual rate nonnegative")
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return monthly_payment * months
    return monthly_payment * (1 - (1 + monthly_rate) ** -months) / monthly_rate


def amortisation_schedule(principal, annual_rate, years):
    """Build a month-by-month schedule of interest and remaining balance."""
    emi = calculate_emi(principal, annual_rate, years)
    balance = principal
    rows = []
    for month in range(1, years * 12 + 1):
        interest = balance * annual_rate / 12
        balance -= emi - interest
        if abs(balance) < 0.01:
            balance = 0
        rows.append((month, round(interest, 2), round(balance, 2)))
    return rows


def application_id():
    """Create an application reference."""
    return f"LN-{secrets.randbelow(90000000) + 10000000}"


def save_application(name, amount, file="loans.json"):
    """Store an application record in the local loan book."""
    app_id = application_id()
    applications[app_id] = {
        "name": name,
        "amount": amount,
        "date": str(datetime.now()),
    }
    with open(file, "w", encoding="utf-8") as application_file:
        json.dump(applications, application_file, indent=2)
    return app_id


def load_applications(file="loans.json"):
    """Load JSON application records from the local loan book."""
    with open(file, "r", encoding="utf-8") as application_file:
        loaded_applications = json.load(application_file)
    if not isinstance(loaded_applications, dict):
        raise ValueError("application file must contain a JSON object")
    applications.clear()
    applications.update(loaded_applications)


def upload_to_bureau(report_path):
    """Upload a report over HTTPS using configured credentials."""
    endpoint = os.environ.get("BUREAU_HTTPS_ENDPOINT", "")
    token = os.environ.get("BUREAU_API_TOKEN", "")
    parsed_endpoint = urlparse(endpoint)
    if (
        parsed_endpoint.scheme != "https"
        or not parsed_endpoint.hostname
        or parsed_endpoint.query
        or parsed_endpoint.fragment
        or not token
    ):
        raise RuntimeError(
            "configure BUREAU_HTTPS_ENDPOINT and BUREAU_API_TOKEN"
        )
    with open(report_path, "rb") as report_file:
        report_data = report_file.read()
    file_name = quote(os.path.basename(report_path))
    upload_path = f"{parsed_endpoint.path.rstrip('/')}/{file_name}"
    connection = HTTPSConnection(
        parsed_endpoint.hostname,
        parsed_endpoint.port or 443,
        context=ssl.create_default_context(),
        timeout=30,
    )
    try:
        connection.request(
            "PUT",
            upload_path,
            body=report_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        response = connection.getresponse()
        if response.status >= 400:
            raise RuntimeError(
                f"bureau upload failed with HTTP {response.status}"
            )
    finally:
        connection.close()


def notify_applicant(email, status):
    """Send an applicant notification through a configured TLS SMTP server."""
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM", smtp_user)
    if not all((smtp_host, smtp_user, smtp_password, sender)):
        raise RuntimeError(
            "configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD, and SMTP_FROM"
        )
    message = EmailMessage()
    message["Subject"] = f"Loan {status}"
    message["From"] = sender
    message["To"] = email
    message.set_content(f"Your loan application status is: {status}")
    with smtplib.SMTP_SSL(
        smtp_host, context=ssl.create_default_context()
    ) as server:
        server.login(smtp_user, smtp_password)
        server.send_message(message)


def interest_saved(principal, annual_rate, years, prepayment):
    """Estimate total interest avoided by reducing principal immediately."""
    if prepayment < 0 or prepayment > principal:
        raise ValueError("prepayment must be between zero and principal")
    original = calculate_emi(principal, annual_rate, years) * years * 12
    reduced = (
        calculate_emi(principal - prepayment, annual_rate, years) * years * 12
    )
    return original - reduced - prepayment


def risk_band(credit_score):
    """Map a credit score to a simple risk label."""
    if credit_score < 300 or credit_score > 900:
        return "INVALID"
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    return "VERY HIGH"


def main():
    """Run a short demonstration without prompting for input."""
    print("EMI for 5L @ 9% for 5 years:", calculate_emi(500000, 0.09, 5))
    print(
        "Eligible (score 760, income 15000, EMIs 12000):",
        check_eligibility(35, 15000, 760, 12000, "personal"),
    )
    print(
        "Eligible (unknown loan type 'crypto'):",
        check_eligibility(30, 80000, 650, 0, "crypto"),
    )
    print("Max loan for income 40000:", max_loan_amount(40000, 5000, 0.09, 5))
    print("Last schedule row:", amortisation_schedule(100000, 0.12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print(
        "Interest saved by prepaying 50000:",
        interest_saved(500000, 0.09, 5, 50000),
    )
    print("Saved as:", save_application("Anil", 500000))
    load_applications()
    print("Applications on file:", len(applications))
    print("Upload to bureau skipped (no network)")


if __name__ == "__main__":
    main()
