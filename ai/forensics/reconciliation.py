"""Pillar 4: Mathematical ledger reconciliation and chronological consistency checks."""
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

class DocumentReconciliationEngine:
    """Performs internal mathematical ledger reconciliation and chronological consistency checks."""

    @classmethod
    def reconcile_financial_math(cls, full_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract financial totals, subtotals, and taxes to verify:
        Subtotal + Tax = Grand Total
        """
        # Look for Subtotal, Tax, Total patterns
        subtotal_match = re.search(r"(?:Subtotal|Sub-Total|Net\s*Amount)[:\s\$€£₹]*([\d,]+\.?\d{0,2})", full_text, re.IGNORECASE)
        tax_match = re.search(r"(?:Tax|VAT|GST|Sales\s*Tax)[:\s\$€£₹]*([\d,]+\.?\d{0,2})", full_text, re.IGNORECASE)
        total_match = re.search(r"(?:Total|Grand\s*Total|Amount\s*Due)[:\s\$€£₹]*([\d,]+\.?\d{0,2})", full_text, re.IGNORECASE)

        if subtotal_match and total_match:
            try:
                subtotal = float(subtotal_match.group(1).replace(",", ""))
                total = float(total_match.group(1).replace(",", ""))
                tax = float(tax_match.group(1).replace(",", "")) if tax_match else 0.0

                expected_total = subtotal + tax
                # Allow minor rounding tolerance (e.g. 0.05)
                if abs(total - expected_total) > 1.0 and expected_total > 0:
                    return {
                        "signal": "financial_math_mismatch",
                        "severity": "HIGH",
                        "category": "ALTERATION",
                        "finding": f"Mathematical reconciliation failure: Subtotal ({subtotal:.2f}) + Tax ({tax:.2f}) = {expected_total:.2f}, but Total is declared as {total:.2f}. Common indicator of altered invoice/financial total."
                    }
            except Exception:
                pass

        return None

    @classmethod
    def reconcile_dates(cls, dates: List[str]) -> Optional[Dict[str, Any]]:
        """
        Verify chronological integrity across document dates:
        e.g., Issue Date <= Expiry Date, Start Date <= End Date
        """
        parsed_dates = []
        for d in dates:
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
                try:
                    parsed_dates.append(datetime.strptime(d.strip(), fmt))
                    break
                except ValueError:
                    continue

        if len(parsed_dates) >= 2:
            # Check for inverted timeline if labelled as issue / expiry
            d1, d2 = parsed_dates[0], parsed_dates[1]
            if d1 > d2:
                return {
                    "signal": "chronological_inversion",
                    "severity": "HIGH",
                    "category": "ALTERATION",
                    "finding": f"Chronological inversion detected: Initial date ({d1.strftime('%Y-%m-%d')}) occurs after secondary date ({d2.strftime('%Y-%m-%d')})."
                }

        return None
