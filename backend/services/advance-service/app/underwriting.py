"""
Underwriting logic for cash advances

Assesses risk and determines eligibility based on:
- Regular income deposits (30+ days history)
- No recent overdrafts/NSF fees
- Minimum account balance
- Previous repayment history
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Tuple
from uuid import UUID


class UnderwritingEngine:
    """Cash advance underwriting engine"""

    # Eligibility thresholds
    MIN_INCOME_HISTORY_DAYS = 30
    MIN_AVERAGE_BALANCE = Decimal("100.00")
    MAX_ADVANCE_AMOUNT = Decimal("250.00")
    MIN_ADVANCE_AMOUNT = Decimal("20.00")
    MIN_REPAYMENT_SUCCESS_RATE = Decimal("80.00")  # 80%

    # Risk scoring weights
    WEIGHT_INCOME_STABILITY = 0.35
    WEIGHT_BALANCE_HISTORY = 0.25
    WEIGHT_OVERDRAFT_HISTORY = 0.20
    WEIGHT_REPAYMENT_HISTORY = 0.20

    @classmethod
    async def check_eligibility(
        cls,
        user_id: UUID,
        banking_data: Dict,
        advance_history: Dict
    ) -> Tuple[bool, Decimal, str, Dict]:
        """
        Check if user is eligible for cash advance

        Returns:
            (is_eligible, max_amount, reason, factors)
        """
        factors = {}

        # Check income stability
        has_regular_income, income_days = cls._check_income_stability(banking_data)
        factors["has_regular_income"] = has_regular_income
        factors["income_history_days"] = income_days

        if not has_regular_income or income_days < cls.MIN_INCOME_HISTORY_DAYS:
            return (
                False,
                Decimal("0.00"),
                f"Need {cls.MIN_INCOME_HISTORY_DAYS}+ days of regular income history",
                factors
            )

        # Check for recent overdrafts
        has_overdrafts = cls._check_overdrafts(banking_data)
        factors["has_recent_overdrafts"] = has_overdrafts

        if has_overdrafts:
            return (
                False,
                Decimal("0.00"),
                "Recent overdraft or NSF fees detected",
                factors
            )

        # Check average balance
        avg_balance = cls._calculate_average_balance(banking_data)
        factors["average_balance"] = avg_balance

        if avg_balance < cls.MIN_AVERAGE_BALANCE:
            return (
                False,
                Decimal("0.00"),
                f"Need minimum average balance of ${cls.MIN_AVERAGE_BALANCE}",
                factors
            )

        # Check previous advance history
        prev_count = advance_history.get("total_advances", 0)
        prev_success_rate = advance_history.get("repayment_success_rate", Decimal("100.00"))
        factors["previous_advance_count"] = prev_count
        factors["previous_repayment_success_rate"] = prev_success_rate

        if prev_count > 0 and prev_success_rate < cls.MIN_REPAYMENT_SUCCESS_RATE:
            return (
                False,
                Decimal("0.00"),
                f"Previous repayment success rate too low: {prev_success_rate}%",
                factors
            )

        # Check for active advances
        if advance_history.get("has_active_advance", False):
            return (
                False,
                Decimal("0.00"),
                "You already have an active advance",
                factors
            )

        # Calculate max advance amount based on risk
        max_amount = cls._calculate_max_advance(avg_balance, prev_success_rate, income_days)

        return (
            True,
            max_amount,
            f"Eligible for up to ${max_amount}",
            factors
        )

    @classmethod
    def _check_income_stability(cls, banking_data: Dict) -> Tuple[bool, int]:
        """
        Check if user has regular income deposits

        Returns: (has_regular_income, days_of_history)
        """
        deposits = banking_data.get("recent_deposits", [])

        if not deposits:
            return False, 0

        # Check for deposits in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_deposits = [
            d for d in deposits
            if d.get("date") and d["date"] > thirty_days_ago
            and d.get("amount", 0) > 500  # Minimum $500 deposits
        ]

        # Need at least 2 deposits in last 30 days
        has_regular_income = len(recent_deposits) >= 2

        # Calculate days of history
        if deposits:
            oldest_deposit = min(deposits, key=lambda d: d.get("date", datetime.utcnow()))
            days_of_history = (datetime.utcnow() - oldest_deposit.get("date", datetime.utcnow())).days
        else:
            days_of_history = 0

        return has_regular_income, days_of_history

    @classmethod
    def _check_overdrafts(cls, banking_data: Dict) -> bool:
        """Check for recent overdrafts or NSF fees"""
        transactions = banking_data.get("recent_transactions", [])

        # Look for overdraft fees in last 60 days
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)

        overdraft_keywords = ["overdraft", "nsf", "insufficient funds", "returned item"]

        for txn in transactions:
            txn_date = txn.get("date")
            if not txn_date or txn_date < sixty_days_ago:
                continue

            description = txn.get("description", "").lower()
            if any(keyword in description for keyword in overdraft_keywords):
                return True

        return False

    @classmethod
    def _calculate_average_balance(cls, banking_data: Dict) -> Decimal:
        """Calculate average balance over last 30 days"""
        balances = banking_data.get("daily_balances", [])

        if not balances:
            return banking_data.get("current_balance", Decimal("0.00"))

        # Get last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_balances = [
            b["balance"] for b in balances
            if b.get("date") and b["date"] > thirty_days_ago
        ]

        if not recent_balances:
            return banking_data.get("current_balance", Decimal("0.00"))

        return sum(recent_balances) / len(recent_balances)

    @classmethod
    def _calculate_max_advance(
        cls,
        avg_balance: Decimal,
        repayment_success_rate: Decimal,
        income_days: int
    ) -> Decimal:
        """
        Calculate maximum advance amount based on risk factors

        More conservative for new users, more generous for established users
        """
        # Base amount on average balance (up to 20%)
        max_amount = min(avg_balance * Decimal("0.20"), cls.MAX_ADVANCE_AMOUNT)

        # Adjust for repayment history
        if repayment_success_rate == Decimal("100.00"):
            # Perfect history gets full amount
            pass
        elif repayment_success_rate >= Decimal("90.00"):
            # Good history gets 80%
            max_amount *= Decimal("0.80")
        else:
            # Acceptable history gets 60%
            max_amount *= Decimal("0.60")

        # Adjust for income history length
        if income_days < 60:
            # New users limited to $100
            max_amount = min(max_amount, Decimal("100.00"))
        elif income_days < 90:
            # 2-3 months history limited to $150
            max_amount = min(max_amount, Decimal("150.00"))

        # Round to nearest $5
        max_amount = (max_amount / 5).quantize(Decimal("1")) * 5

        # Ensure within bounds
        max_amount = max(cls.MIN_ADVANCE_AMOUNT, min(max_amount, cls.MAX_ADVANCE_AMOUNT))

        return max_amount

    @classmethod
    def calculate_risk_score(
        cls,
        has_regular_income: bool,
        avg_balance: Decimal,
        has_overdrafts: bool,
        repayment_success_rate: Decimal
    ) -> Decimal:
        """
        Calculate risk score (0-100, lower is better)

        Used for monitoring and future underwriting improvements
        """
        score = Decimal("0.00")

        # Income stability (0-35 points)
        if not has_regular_income:
            score += Decimal("35.00")

        # Balance history (0-25 points)
        if avg_balance < Decimal("100.00"):
            score += Decimal("25.00")
        elif avg_balance < Decimal("500.00"):
            score += Decimal("15.00")
        elif avg_balance < Decimal("1000.00"):
            score += Decimal("5.00")

        # Overdraft history (0-20 points)
        if has_overdrafts:
            score += Decimal("20.00")

        # Repayment history (0-20 points)
        if repayment_success_rate < Decimal("80.00"):
            score += Decimal("20.00")
        elif repayment_success_rate < Decimal("90.00"):
            score += Decimal("10.00")
        elif repayment_success_rate < Decimal("100.00"):
            score += Decimal("5.00")

        return score
