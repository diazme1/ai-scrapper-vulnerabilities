#from .scorer import Scores

class RiskClassifier:

    def __init__(self, config_path: str):
        self.scorer = Scorer(config_path)

    # def __calculate_score(self, probabilities):

    # mapping = {

    #     "LOW":25,

    #     "MEDIUM":50,

    #     "HIGH":75,

    #     "CRITICAL":100

    # }

    # score = 0

    # for probability, label in zip(probabilities, self.encoder.classes_):
    #     score += probability * mapping[label]

    # return score


    # def process_profile(self, profile: dict):

    #     score = scorer.calculate(profile)

    #     return {
    #         "risk": risk,
    #         "score": score
    #     }

    

    # def train(self, dataset: pd.DataFrame):
    #     ...

    # def predict(self, profile: pd.Series):
    #     ...