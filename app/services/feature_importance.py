from app.models.boost_model import ForwardModel
from app.schemas.response import Recommendation
import numpy as np

class FeatureRecommender:
    _feature_thresholds = {
        'bc_open_to_buy': (11394.25, 711140.0),
        'revol_util': (49.91, 892.0),
        'pct_tl_nvr_dlq': (93.92, 100.0),
        'number_of_derogatory_records': (0.20, 86.0),
        'number_of_collections': (232.71, 9152545.0),
        'mo_sin_old_rev_tl_op': (181.48, 999.0),
        'num_actv_bc_tl': (3.66, 50.0),
        'tot_hi_cred_lim': (178242.73, 9999999.0),
        'accounts_with_75_percent_limit': (42.30, 100.0),
        'credits_overdue_120_days': (0.48, 58.0),
        'mo_sin_rcnt_rev_tl_op': (14.02, 547.0),
        'num_actv_rev_tl': (5.61, 72.0),
        'mo_sin_old_il_acct': (125.69, 999.0),
        'credits_taken_last_2_years': (4.51, 64.0),
        'total_il_high_credit_limit': (43732.01, 2118996.0),
        'bc_util': (57.46, 339.0),
        'monthly_debt_payments': (18.33, 999.0),
        'avg_cur_bal': (13547.77, 958084.0),
        'total_income': (77992.42, 110000000.0),
        'credits_overdue_30_days': (0.31, 58.0)
    }

    _negative_features = ['credits_overdue_120_days', 'number_of_derogatory_records', 'number_of_collections',
                          'credits_taken_last_2_years' 'credits_overdue_30_days']

    def __init__(self, feature_names):
        self.model = ForwardModel()
        self.feature_names = feature_names

    def get_recommendations(self, recommendations, feat_name, importance, good_threshold, max_val, current_value):
        impact = ((good_threshold - current_value) / max_val) * importance
        message = None

        if feat_name in self._negative_features:
            if current_value > good_threshold:
                message = f"Зменшіть {feat_name} з {float(current_value):.2f} до твердої відмітки {float(good_threshold):.2f}. Людям з таким показником частіше одобрюють кредити."
                recommendations.append(Recommendation(
                    feat_name=feat_name,
                    current_value=float(current_value),
                    target_value=float(good_threshold),
                    importance=float(importance),
                    impact=float(impact),
                    message=message
                ))
        else:
            if current_value < good_threshold:
                message = f"Покращіть {feat_name} з {float(current_value):.2f} до твердої відмітки {float(good_threshold):.2f}. Людям з таким показником частіше одобрюють кредити."
                recommendations.append(Recommendation(
                    feat_name=feat_name,
                    current_value=float(current_value),
                    target_value=float(good_threshold),
                    importance=float(importance),
                    impact=float(impact),
                    message=message
                ))
        
    def analyze_features(self, user_data):        
        # Analyze each feature's contribution
        recommendations = []
        for feat_name, importance in zip(self.feature_names, self.model.feature_importances):
            if feat_name not in self._feature_thresholds:
                continue
            
            if importance > 0.05:  # Only consider important features
                good_threshold, max_val = self._feature_thresholds[feat_name]
                current_value = user_data[feat_name]
         
                self.get_recommendations(recommendations, feat_name, importance, good_threshold, max_val, current_value)

        # Sort by impact
        recommendations.sort(key=lambda x: abs(x.impact), reverse=True)
        return recommendations