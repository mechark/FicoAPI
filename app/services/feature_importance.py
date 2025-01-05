from typing import List, Dict, Optional

from app.models.boost_model import ForwardModel
from app.schemas.response import NotNeedImprovement, Recommendation
from app.schemas.feature_config import FeatureConfig, FeatureStatus


class FeatureRecommender:
    """Analyzes user features and provides recommendations for credit approval."""

    _special_features = {
        "home_ownership_ANY": "Наявність будь-якого власного житла",
        "home_ownership_MORTGAGE": "Іпотечний кредит",
        "home_ownership_OWN": "Власне житло",
    }

    def __init__(self, feature_names: List[str]):
        self.model = ForwardModel()
        self.feature_names = feature_names
        self._initialize_feature_configs()

    def _initialize_feature_configs(self) -> None:
        self.feature_configs: Dict[str, FeatureConfig] = {
            "total_credit_limit": FeatureConfig(
                threshold=(178242.73, 9999999.0),
                ukrainian_name="Загальний кредитний ліміт",
                explanation="Більший кредитний ліміт показує довіру банків та вашу платоспроможність. Для покращення: вчасно сплачуйте поточні кредити та підтримуйте стабільний дохід",
            ),
            "available_credit_limit": FeatureConfig(
                threshold=(178242.73, 9999999.0),
                ukrainian_name="Доступний кредит",
                explanation="Наявність вільного кредитного ліміту свідчить про розумне використання кредитів. Намагайтеся використовувати не більше 30% доступного ліміту",
            ),
            "used_credit_amount": FeatureConfig(
                threshold=(49.91, 892.0),
                ukrainian_name="Використані кредитні кошти",
                status=FeatureStatus(is_negative=True, can_improve=False),
                explanation="Висока використана сума кредиту може вказувати на фінансові труднощі. Спробуйте поступово зменшити заборгованість, почавши з карток з найвищими відсотками",
            ),
            "total_card_balance": FeatureConfig(
                threshold=(0.0, 9999999.0),
                ukrainian_name="Загальний баланс на картках",
                status=FeatureStatus(is_negative=True, can_improve=True),
                explanation="Великий баланс на картках збільшує ризик неповернення коштів. Рекомендуємо створити план погашення, починаючи з карток з найвищою процентною ставкою",
            ),
            "pct_tl_nvr_dlq": FeatureConfig(
                threshold=(93.92, 100.0),
                ukrainian_name="Відсоток рахунків без прострочень",
                explanation="Високий відсоток вчасних платежів покращує кредитний рейтинг. Налаштуйте автоматичні платежі та календар сплат, щоб не пропускати терміни",
            ),
            "accounts_with_late_payments": FeatureConfig(
                threshold=(0, 50.0),
                ukrainian_name="Рахунки з простроченнями",
                explanation="Прострочені платежі негативно впливають на кредитну історію. Встановіть нагадування про платежі та тримайте резервний фонд для своєчасної оплати",
            ),
            "accounts_with_75_percent_limit": FeatureConfig(
                threshold=(42.30, 100.0),
                ukrainian_name="Рахунки з більше ніж 75% доступного кредиту",
                explanation="Високе використання ліміту може вказувати на фінансові труднощі. Намагайтеся тримати використання кредитного ліміту нижче 30%",
                status=FeatureStatus(is_negative=True, can_improve=True),
            ),
            "number_of_derogatory_records": FeatureConfig(
                threshold=(0, 86.0),
                ukrainian_name="Кількість негативних записів",
                explanation="Негативні записи значно знижують кредитний рейтинг. Уникайте нових порушень та працюйте над погашенням існуючих заборгованостей",
            ),
            "credits_overdue_120_days": FeatureConfig(
                threshold=(0, 58.0),
                ukrainian_name="Прострочення понад 120 днів",
                explanation="Тривалі прострочення серйозно впливають на кредитний рейтинг. Зверніться до кредиторів для розробки плану реструктуризації боргу",
                status=FeatureStatus(is_negative=True, can_improve=False),
            ),
            "total_il_high_credit_limit": FeatureConfig(
                threshold=(43732.01, 2118996.0),
                ukrainian_name="Загальний ліміт по інстальментних кредитах",
                explanation="Високий ліміт показує довіру банків. Підтримуйте стабільний дохід та вчасно сплачуйте поточні кредити для збільшення лімітів",
            ),
            "bc_util": FeatureConfig(
                threshold=(57.46, 339.0),
                ukrainian_name="Використання кредитних карт",
                explanation="Помірне використання карт вказує на фінансову дисципліну. Тримайте баланс нижче 30% від ліміту та вчасно сплачуйте рахунки",
            ),
            "monthly_debt_payments": FeatureConfig(
                threshold=(18.33, 999.0),
                ukrainian_name="Щомісячні виплати боргу",
                explanation="Високі виплати збільшують ризик. Створіть бюджет та план погашення, починаючи з боргів з найвищими відсотками",
            ),
            "total_income": FeatureConfig(
                threshold=(77992.42, 110000000.0),
                ukrainian_name="Сукупний місячний дохід",
                explanation="Вищий дохід покращує співвідношення боргу до доходу. Розгляньте можливості додаткового заробітку або підвищення кваліфікації",
            ),
            "mo_sin_rcnt_rev_tl_op": FeatureConfig(
                threshold=(14.02, 547.0),
                ukrainian_name="Місяців з останнього відкриття револьверного рахунку",
                explanation="Довший період без нових рахунків показує стабільність. Утримайтесь від відкриття нових кредитів протягом 6-12 місяців",
            ),
            "home_ownership_ANY": FeatureConfig(
                threshold=(1.0, 1.0),
                ukrainian_name="Власність на житло",
                explanation="Наявність житла позитивно впливає на рейтинг. Розгляньте можливість придбання житла або оформлення іпотеки при стабільному доході",
            ),
            "number_of_collections": FeatureConfig(
                threshold=(0, 1000),
                ukrainian_name="Кількість боргів у колекторів",
                status=FeatureStatus(is_negative=True, can_improve=True),
                explanation="Борги, передані колекторам, негативно впливають на кредитний рейтинг. Спробуйте домовитися з кредиторами про реструктуризацію боргу або розгляньте можливість консультування з фінансовим експертом для вирішення проблеми",
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

    def _create_message(self, config: FeatureConfig, feat_name: str) -> str:
        if not config.status.can_improve:
            message = (
                "На жаль, цей показник вже не вдасться покращити. " + config.explanation
            )
        else:
            if feat_name in self._special_features:
                message = f"{config.explanation}"
            else:
                action = "знизити" if config.status.is_negative else "підвищити"
                message = f"Радимо {action} цей показник. {config.explanation}"

        return message

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

        if importance > 0.05:
            message = self._create_message(config, feat_name)

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

    def analyze_features(
        self, user_data: Dict[str, float]
    ) -> List[Recommendation] | NotNeedImprovement:
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
            return NotNeedImprovement(
                message="Ваш кредитний рейтинг вже на високому рівні, радимо продовжувати в тому ж дусі!"
            )

        return sorted(recommendations, key=lambda x: abs(x.impact), reverse=True)
