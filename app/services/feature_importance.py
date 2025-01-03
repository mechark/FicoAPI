from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

from app.models.boost_model import ForwardModel
from app.schemas.response import Recommendation


@dataclass
class FeatureConfig:
    """Configuration for a feature including its threshold and Ukrainian translation."""

    threshold: Tuple[float, float]
    ukrainian_name: str
    is_negative: bool = False


class FeatureRecommender:
    """Analyzes user features and provides recommendations for credit approval."""

    def __init__(self, feature_names: List[str], total_accounts: int):
        self.model = ForwardModel()
        self.feature_names = feature_names
        self._initialize_feature_configs(total_accounts)

    def _initialize_feature_configs(self, total_accounts: int) -> None:
        """Initialize feature configurations with thresholds and translations."""
        self.feature_configs: Dict[str, FeatureConfig] = {
            # Credit-related features
            "total_credit_limit": FeatureConfig(
                (178242.73, 9999999.0), "Загальний кредитний ліміт"
            ),
            "available_credit_limit": FeatureConfig(
                (178242.73, 9999999.0), "Доступний кредитний ліміт"
            ),
            "used_credit_amount": FeatureConfig(
                (49.91, 892.0), "Використана кредитна сума", is_negative=True
            ),
            "total_card_balance": FeatureConfig(
                (0.0, 9999999.0), "Загальний баланс на картках", is_negative=True
            ),
            # Account health metrics
            "pct_tl_nvr_dlq": FeatureConfig(
                (93.92, 100.0), "Відсоток рахунків без прострочень"
            ),
            "accounts_with_late_payments": FeatureConfig(
                (total_accounts, 50.0),
                "Кількість рахунків на яких коли небудь було протерміновано виплату",
            ),
            "accounts_with_75_percent_limit": FeatureConfig(
                (42.30, 100.0),
                "Кількість рахунків, де доступно > 75% кредитного ліміту",
                is_negative=True,
            ),
            # Negative indicators
            "number_of_derogatory_records": FeatureConfig(
                (0.20, 86.0),
                "Кількість принизливих публічних записів",
                is_negative=True,
            ),
            "number_of_collections": FeatureConfig(
                (232.71, 9152545.0),
                "Кількість заборгованостей переданих колекторам",
                is_negative=True,
            ),
            "credits_overdue_120_days": FeatureConfig(
                (0.48, 58.0),
                "Кількість прострочених кредитів на 120 днів і більше",
                is_negative=True,
            ),
            "credits_overdue_30_days": FeatureConfig(
                (0.31, 58.0),
                "Кількість прострочених кредитів на 30 днів і більше",
                is_negative=True,
            ),
            # Financial metrics
            "total_il_high_credit_limit": FeatureConfig(
                (43732.01, 2118996.0), "Загальний ліміт по інстальментних кредитах"
            ),
            "bc_util": FeatureConfig((57.46, 339.0), "Використання кредитних карт"),
            "monthly_debt_payments": FeatureConfig(
                (18.33, 999.0), "Щомісячні виплати боргу", is_negative=True
            ),
            "avg_cur_bal": FeatureConfig(
                (13547.77, 958084.0), "Середній поточний баланс"
            ),
            "total_income": FeatureConfig((77992.42, 110000000.0), "Сумарний дохід"),
            # Other metrics
            "mo_sin_rcnt_rev_tl_op": FeatureConfig(
                (14.02, 547.0), "Місяців з останнього відкриття револьверного рахунку"
            ),
            "num_actv_rev_tl": FeatureConfig(
                (5.61, 72.0), "Кількість активних револьверних рахунків"
            ),
            "mo_sin_old_il_acct": FeatureConfig(
                (125.69, 999.0),
                "Місяців з відкриття найстарішого інстальментного рахунку",
            ),
            "home_ownership_ANY": FeatureConfig((1.0, 1.0), "Власність на житло"),
        }

    def _calculate_impact(
        self,
        current_value: float,
        good_threshold: float,
        max_val: float,
        importance: float,
    ) -> float:
        """Calculate the impact score for a feature."""
        return ((good_threshold - current_value) / max_val) * importance

    def _create_recommendation(
        self,
        feat_name: str,
        current_value: float,
        good_threshold: float,
        max_val: float,
        importance: float,
        config: FeatureConfig,
    ) -> Optional[Recommendation]:
        """Create a recommendation if the feature needs improvement."""
        needs_improvement = (
            (current_value > good_threshold)
            if config.is_negative
            else (current_value < good_threshold)
        )

        if not needs_improvement:
            return None

        action = "Зменщіть" if config.is_negative else "Збільщіть"
        message = f"{action} '{config.ukrainian_name}'. Людям з такими показниками частіше одобрюють видачу кредиту."

        impact = self._calculate_impact(
            current_value, good_threshold, max_val, importance
        )

        return Recommendation(
            feat_name=feat_name,
            current_value=int(current_value),
            target_value=int(good_threshold),
            importance=float(importance),
            impact=float(impact),
            message=message,
        )

    def analyze_features(self, user_data: Dict[str, float]) -> List[Recommendation]:
        """Analyze user features and return sorted recommendations."""
        recommendations = []

        for feat_name, importance in zip(
            self.feature_names, self.model.feature_importances
        ):
            if feat_name not in self.feature_configs or importance <= 0.0:
                continue

            config = self.feature_configs[feat_name]
            good_threshold, max_val = config.threshold
            current_value = user_data[feat_name]

            recommendation = self._create_recommendation(
                feat_name=feat_name,
                current_value=current_value,
                good_threshold=good_threshold,
                max_val=max_val,
                importance=importance,
                config=config,
            )

            if recommendation:
                recommendations.append(recommendation)

        return sorted(recommendations, key=lambda x: abs(x.impact), reverse=True)
