# from pathlib import Path
# import yaml


# class Scorer:

#     def __init__(self, config_path: str):

#         with open(Path(config_path), "r", encoding="utf-8") as file:
#             config = yaml.safe_load(file)

#         self.scores = config["scores"]
#         self.levels = config["levels"]

#     def calcular_score(self, profile: dict) -> int:

#         score = 0

#         for aspecto, valor in profile.items():

#             if aspecto == "cve":
#                 score += valor * self.scores["cve"]

#             elif aspecto == "failed_security_headers":
#                 score += valor * self.scores["failed_security_headers"]

#             elif valor:
#                 score += self.scores.get(aspecto, 0)

#         return min(score, 100)

#     def get_risk_level(self, score: int) -> str:
#         """
#         Devuelve el nivel de riesgo correspondiente al score.
#         """

#         if score <= self.levels["LOW"]:
#             return "LOW"

#         if score <= self.levels["MEDIUM"]:
#             return "MEDIUM"

#         if score <= self.levels["HIGH"]:
#             return "HIGH"

#         return "CRITICAL"

#     def process_profile(self, profile: dict) -> tuple[int, str]:
#         """
#         Procesa un perfil completo.

#         Returns
#         -------
#         tuple[int, str]
#             (score, risk_level)
#         """

#         score = self.calculate_score(profile)

#         return score, self.get_risk_level(score)