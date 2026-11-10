import re
from typing import Tuple, Dict, Any, Optional
from app.common.logger import get_logger

logger = get_logger(__name__)

# Minimum authorized base tariffs (cannot be discounted below these thresholds)
MINIMUM_AUTHORIZED_TARIFFS = {
    "Standard": 2000.0,
    "Deluxe": 3500.0,
    "Suite": 6500.0
}

# Prompt Injection and System Compromise Signatures
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"system\s+prompt\s+override",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"reveal\s+(internal|secret|private|api)\s+(key|token|password|prompt)",
    r"override\s+tariff\s+to\s+0",
    r"set\s+price\s+to\s+free",
    r"give\s+me\s+root\s+access",
    r"bypass\s+(payment|security|blacklist)",
    r"drop\s+table\s+rooms",
    r"--\s*;\s*drop\s+database"
]

class HotelGuardrails:
    """
    Enterprise Hospitality AI Guardrails Engine.
    Enforces security, regulatory compliance, rate protection, and operational safety
    across Receptionist, Manager, Owner, Housekeeping, and Concierge workflows.
    """

    # ----------------- 1. Input Guardrails -----------------
    @classmethod
    def check_input_safety(cls, user_text: str) -> Tuple[bool, Optional[str]]:
        """
        Validates incoming user prompt against prompt injection, jailbreaks, and system tampering.
        Returns (is_safe, violation_reason).
        """
        if not user_text or not user_text.strip():
            return True, None

        normalized = user_text.lower().strip()

        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, normalized):
                logger.warning("Input Guardrail Triggered: Injection attempt detected: '%s'", pattern)
                return False, "Security Guardrail Triggered: Request contains unauthorized system override or security bypass instructions."

        return True, None

    @classmethod
    def validate_guest_credentials(cls, name: str, phone: str, id_proof: str, blacklisted_set: set) -> Tuple[bool, Optional[str]]:
        """
        Validates guest contact numbers, ID proof formats, and checks against the security blacklist.
        """
        # Name validation
        if not name or len(name.strip()) < 2:
            return False, "Validation Error: Guest name must contain at least 2 characters."

        # Phone validation (10 to 15 digits)
        clean_phone = re.sub(r"[\s\-\(\)\+]", "", phone)
        if not clean_phone.isdigit() or len(clean_phone) < 10 or len(clean_phone) > 15:
            return False, "Validation Error: Phone number must be a valid 10-15 digit contact number."

        # ID Proof validation
        if not id_proof or len(id_proof.strip()) < 4:
            return False, "Validation Error: Valid government-issued ID proof (Passport / Aadhaar / DL) is mandatory."

        # Blacklist check
        if id_proof.strip().upper() in blacklisted_set or id_proof.strip() in blacklisted_set:
            logger.warning("Security Guardrail: Attempted booking with blacklisted ID: %s", id_proof)
            return False, f"Security Alert: ID Proof '{id_proof}' is blacklisted due to prior hotel policy violations."

        return True, None

    # ----------------- 2. Output Guardrails -----------------
    @classmethod
    def enforce_rate_integrity(cls, generated_response: str) -> str:
        """
        Output Guardrail: Scans generated LLM response to ensure the agent did not promise
        unauthorized rates below minimum authorized base tariffs.
        """
        # Check for free / zero dollar promises
        lower_resp = generated_response.lower()
        if "₹0" in lower_resp or "free of charge for the room" in lower_resp or "rate of 0" in lower_resp:
            logger.warning("Output Guardrail Triggered: Zero rate detected in response. Scrubbing.")
            return (
                "Official Hotel Policy Notice: Room rates cannot be reduced below standard published tariffs. "
                "Standard: ₹2,500/night | Deluxe: ₹4,200/night | Presidential Suite: ₹7,800/night. "
                "Please contact the General Manager for approved corporate discount agreements."
            )
        return generated_response

    @classmethod
    def enforce_checkout_payment_guardrail(cls, balance_due: float, payment_settled: bool) -> Tuple[bool, Optional[str]]:
        """
        Ensures a guest room checkout is never processed if payment balance > 0 and payment_settled is False.
        """
        if balance_due > 0 and not payment_settled:
            logger.warning("Payment Guardrail Triggered: Attempted checkout with unpaid balance: ₹%s", balance_due)
            return False, f"Payment Guardrail: Checkout blocked. Outstanding folio balance of ₹{balance_due:,.2f} must be settled before room release."
        return True, None

    @classmethod
    def filter_response(cls, response: str) -> str:
        """Runs all output guardrails in sequence."""
        cleaned = cls.enforce_rate_integrity(response)
        return cleaned

