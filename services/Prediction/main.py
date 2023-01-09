import os

import joblib

from services.utils.config import prediction_model_path

CWD = os.path.dirname(os.path.abspath(__file__))


def get_prediction(quote: str, path=f'{CWD}/{prediction_model_path}') -> str:
    model = open(path, 'rb')
    pipeline = joblib.load(model)
    labels_text = ['aspirations', 'emotional', 'personal', 'thoughtful', 'work']
    ans = pipeline.predict([quote])
    return labels_text[int(ans)]
