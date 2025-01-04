from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Dict, Any

class UserData(BaseModel):
    total_credit_limit: float = Field(..., ge=0)
    used_credit_amount: float = Field(..., ge=0)
    available_credit_limit: float = Field(..., ge=0)
    accounts_with_late_payments: int = Field(..., ge=0)
    total_accounts: int = Field(..., ge=1)
    number_of_derogatory_records: int = Field(..., ge=0)
    number_of_collections: int = Field(..., ge=0)
    months_since_first_credit: int = Field(..., ge=0)
    accounts_with_75_percent_limit: int = Field(..., ge=0)
    credits_overdue_120_days: int = Field(..., ge=0)
    total_taken_credits: int = Field(..., ge=0)
    credits_taken_last_2_years: int = Field(..., ge=0)
    total_card_balance: float = Field(..., ge=0)
    total_income: float = Field(..., ge=0)
    monthly_debt_payments: float = Field(..., ge=0)
    credits_overdue_30_days: int = Field(..., ge=0)
    home_ownership_RENT: bool = Field(default=False)
    home_ownership_MORTGAGE: bool = Field(default=False)
    home_ownership_OWN: bool = Field(default=False)
    home_ownership_ANY: bool = Field(default=False)
    home_ownership_OTHER: bool = Field(default=False)
    home_ownership_NONE: bool = Field(default=False)


class InputFeatures(UserData):
    @computed_field
    @property
    def bc_open_to_buy(self) -> int:
        return int(self.total_credit_limit - self.used_credit_amount)

    @computed_field
    @property
    def revol_util(self) -> int:
        return (
            int(
                self.used_credit_amount / self.total_credit_limit
                if self.total_credit_limit != 0
                else 1e-6
            )
            * 100
        )

    @computed_field
    @property
    def pct_tl_nvr_dlq(self) -> int:
        accounts_without_late_payments = self.total_accounts - self.accounts_with_late_payments
        return int(accounts_without_late_payments / self.total_accounts) * 100

    @computed_field
    @property
    def mo_sin_rcnt_rev_tl_op(self) -> int:  # months_since_first_credit
        return self.months_since_first_credit

    @computed_field
    @property
    def num_actv_rev_tl(self) -> int:  # total_accounts
        return self.total_accounts

    @computed_field
    @property
    def mo_sin_old_il_acct(self) -> int:  # months_since_first_credit
        return self.months_since_first_credit

    @computed_field
    @property
    def total_il_high_credit_limit(self) -> int:  # total_credit_limit
        return self.total_credit_limit

    @computed_field
    @property
    def mo_sin_old_rev_tl_op(self) -> int:
        return self.months_since_first_credit

    @computed_field
    @property
    def bc_util(self) -> int:
        return (
            int(
                self.used_credit_amount / self.total_credit_limit
                if self.total_credit_limit != 0
                else 1e-6
            )
            * 100
        )

    @computed_field
    @property
    def avg_cur_bal(self) -> int:
        return int(self.total_card_balance / self.total_accounts)
    
    @computed_field
    @property
    def dti(self) -> int:
        return int(self.monthly_debt_payments / self.total_income if self.total_income != 0 else 1e-6 * 100)

    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=("model_",),
    )

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        ordered_fields = [
            "bc_open_to_buy",
            "revol_util",
            "pct_tl_nvr_dlq",
            "number_of_derogatory_records",
            "number_of_collections",
            "mo_sin_old_rev_tl_op",
            "num_actv_rev_tl",
            "total_credit_limit",
            "accounts_with_75_percent_limit",
            "credits_overdue_120_days",
            "mo_sin_rcnt_rev_tl_op",
            "total_accounts",
            "mo_sin_old_il_acct",
            "credits_taken_last_2_years",
            "total_il_high_credit_limit",
            "bc_util",
            "dti",
            "avg_cur_bal",
            "total_income",
            "credits_overdue_30_days",
            "home_ownership_RENT",
            "home_ownership_MORTGAGE",
            "home_ownership_OWN",
            "home_ownership_ANY",
            "home_ownership_OTHER",
            "home_ownership_NONE",
        ]
        return {k: data[k] for k in ordered_fields}
