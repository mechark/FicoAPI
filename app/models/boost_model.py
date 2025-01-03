import pickle
import os


class ForwardModel:
    _instance = None
    _model = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ForwardModel, cls).__new__(cls)
            try:
                model_path = os.path.join(os.path.dirname(__file__), "xgb_model_2.pkl")
                with open(model_path, "rb") as f:
                    cls._model = pickle.load(f)
            except FileNotFoundError as e:
                raise RuntimeError(f"Model file not found at {model_path}") from e
        return cls._instance

    def predict(self, data):
        return self._model.predict(data)

    @property
    def feature_importances(self):
        return self._model.feature_importances_
