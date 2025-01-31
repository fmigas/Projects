
from pydantic import BaseModel


class Operator(BaseModel):

    models: dict = {}

    def register_model(self, marker: str, model: BaseModel):
        """
        Register a model with the operator
        :param marker: np. 'txt' albo 'http'
        :param model: właściwy model do obrótki danych danego typu
        :return:
        """
        self.models[marker] = model

    def get_model(self, marker: str) -> BaseModel:
        """
        Get a model from the operator
        :param marker: np. 'txt' albo 'http'
        :return:
        """
        return self.models.get(marker)

    @property
    def registered_models(self):
        return list(self.models.keys())
