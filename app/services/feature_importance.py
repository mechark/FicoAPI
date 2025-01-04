from typing import List, Dict, Optional

from app.models.boost_model import ForwardModel
from app.schemas.response import NotNeedImprovement, Recommendation
from app.schemas.feature_config import FeatureConfig, FeatureStatus

class FeatureRecommender:
    """Analyzes user features and provides recommendations for credit approval."""

    _special_features = {
        "home_ownership_ANY": "Наявність власного житла",
        "home_ownership_MORTGAGE": "Іпотечний кредит",
        "home_ownership_OWN": "Власне житло",
    }

    def __init__(self, feature_names: List[str], total_accounts: int):
        self.model = ForwardModel()
        self.feature_names = feature_names
        self._initialize_feature_configs(total_accounts)

    def _initialize_feature_configs(self, total_accounts: int) -> None:
        """Initialize feature configurations with thresholds and translations."""
        self.feature_configs: Dict[str, FeatureConfig] = {
            # Credit-related features
            "total_credit_limit": FeatureConfig(
                threshold=(178242.73, 9999999.0), 
                ukrainian_name="Загальний кредитний ліміт",
                explanation="Більший кредитний ліміт показує довіру банків та вашу платоспроможність"
            ),
            "available_credit_limit": FeatureConfig(
                threshold=(178242.73, 9999999.0), 
                ukrainian_name="Доступний кредитний ліміт",
                explanation="Наявність вільного кредитного ліміту свідчить про розумне використання кредитів"
            ),
            "used_credit_amount": FeatureConfig(
                threshold=(49.91, 892.0), 
                ukrainian_name="Використана кредитна сума", 
                status=FeatureStatus(is_negative=True, can_improve=False),
                explanation="Висока використана сума кредиту може вказувати на фінансові труднощі"
            ),
            "total_card_balance": FeatureConfig(
                threshold=(0.0, 9999999.0), 
                ukrainian_name="Загальний баланс на картках", 
                status=FeatureStatus(is_negative=True, can_improve=True),
                explanation="Великий баланс на картках збільшує ризик неповернення коштів"
            ),
            # Account health metrics
            "pct_tl_nvr_dlq": FeatureConfig(
                threshold=(93.92, 100.0), 
                ukrainian_name="Відсоток рахунків без прострочень",
                explanation="Високий відсоток вчасних платежів покращує кредитний рейтинг"
            ),
            "accounts_with_late_payments": FeatureConfig(
                threshold=(0, 50.0),
                ukrainian_name="Кількість рахунків на яких коли небудь було протерміновано виплату",
                explanation="Прострочені платежі негативно впливають на кредитну історію",
                status=FeatureStatus(is_negative=True, can_improve=False),
            ),
            "accounts_with_75_percent_limit": FeatureConfig(
                threshold=(42.30, 100.0),
                ukrainian_name="Кількість рахунків, де доступно > 75% кредитного ліміту",
                status=FeatureStatus(is_negative=True, can_improve=True),
                explanation="Високе використання ліміту може вказувати на фінансові труднощі"
            ),
            # Negative indicators
            "number_of_derogatory_records": FeatureConfig(
                threshold=(0.20, 86.0),
                ukrainian_name="Кількість принизливих публічних записів",
                status=FeatureStatus(is_negative=True, can_improve=False),
                explanation="Негативні записи значно знижують кредитний рейтинг"
            ),
            "number_of_collections": FeatureConfig(
                threshold=(232.71, 9152545.0),
                ukrainian_name="Кількість заборгованостей переданих колекторам",
                status=FeatureStatus(is_negative=True, can_improve=False),
                explanation="Передача боргів колекторам серйозно погіршує кредитну історію"
            ),
            "credits_overdue_120_days": FeatureConfig(
                threshold=(0.48, 58.0),
                ukrainian_name="Кількість прострочених кредитів на 120 днів і більше",
                status=FeatureStatus(is_negative=True, can_improve=False),
                explanation="Тривалі прострочення серйозно впливають на кредитний рейтинг"
            ),
            "credits_overdue_30_days": FeatureConfig(
                threshold=(0.31, 58.0),
                ukrainian_name="Кількість прострочених кредитів на 30 днів і більше",
                status=FeatureStatus(is_negative=True, can_improve=False),
                explanation="Навіть короткі прострочення негативно впливають на рейтинг"
            ),
            # Financial metrics
            "total_il_high_credit_limit": FeatureConfig(
                threshold=(43732.01, 2118996.0), 
                ukrainian_name="Загальний ліміт по інстальментних кредитах",
                explanation="Високий ліміт по інстальментних кредитах показує довіру банків"
            ),
            "bc_util": FeatureConfig(
                threshold=(57.46, 339.0), 
                ukrainian_name="Використання кредитних карт",
                explanation="Помірне використання кредитних карт вказує на фінансову дисципліну"
            ),
            "monthly_debt_payments": FeatureConfig(
                threshold=(18.33, 999.0), 
                ukrainian_name="Щомісячні виплати боргу", 
                explanation="Високі щомісячні виплати зменшують ризик неповернення"
            ),
            "avg_cur_bal": FeatureConfig(
                threshold=(13547.77, 958084.0), 
                ukrainian_name="Середній поточний баланс",
                explanation="Стабільний середній баланс показує фінансову стійкість"
            ),
            "total_income": FeatureConfig(
                threshold=(77992.42, 110000000.0), 
                ukrainian_name="Сумарний дохід",
                explanation="Вищий дохід покращує співвідношення боргу до доходу"
            ),
            # Other metrics
            "mo_sin_rcnt_rev_tl_op": FeatureConfig(
                threshold=(14.02, 547.0), 
                ukrainian_name="Місяців з останнього відкриття револьверного рахунку",
                explanation="Довший період без нових рахунків показує фінансову стабільність"
            ),
            "num_actv_rev_tl": FeatureConfig(
                threshold=(5.61, 72.0), 
                ukrainian_name="Кількість активних револьверних рахунків",
                explanation="Помірна кількість активних рахунків показує досвід користування кредитами"
            ),
            "mo_sin_old_il_acct": FeatureConfig(
                threshold=(125.69, 999.0),
                ukrainian_name="Місяців з відкриття найстарішого інстальментного рахунку",
                explanation="Довша кредитна історія підвищує довіру кредиторів"
            ),
            "home_ownership_ANY": FeatureConfig(
                threshold=(1.0, 1.0), 
                ukrainian_name="Власність на житло",
                explanation="Наявність власного житла позитивно впливає на кредитний рейтинг"
            ),
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
            if config.status.is_negative
            else (current_value < good_threshold)
        )

        if not needs_improvement:
            return None

        if not config.status.can_improve:
            message = "На жаль, цей показник вже не вдасться покращити. " + config.explanation
        else:
            if feat_name in self._special_features:
                message = f"{config.explanation}"
            else:
                action = "знизити" if config.status.is_negative else "підвищити"
                message = f"Радимо {action} цей показник. {config.explanation}"

        impact = self._calculate_impact(
            current_value, good_threshold, max_val, importance
        )

        return Recommendation(
            feat_name=self.feature_configs[feat_name].ukrainian_name,
            current_value=int(current_value),
            target_value=int(good_threshold),
            importance=float(importance),
            impact=float(impact),
            message=message,
        )

    def analyze_features(self, user_data: Dict[str, float]) -> List[Recommendation] | NotNeedImprovement:
        """Analyze user features and return sorted recommendations."""
        recommendations = []

        for feat_name, importance in zip(
            self.feature_names, self.model.feature_importances
        ):
            if feat_name not in self.feature_configs:
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

        if not recommendations:
            return NotNeedImprovement(message="Ваш кредитний рейтинг вже на високому рівні, радимо продовжувати в тому ж дусі!")
        
        return sorted(recommendations, key=lambda x: abs(x.impact), reverse=True)
