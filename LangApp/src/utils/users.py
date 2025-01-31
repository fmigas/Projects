from pydantic import BaseModel, field_validator
from src.config import settings
from src.utils.mongo_functions import save_data_to_mongodb


class User(BaseModel):
    name: str
    level: str
    native_language: str
    learned_language: str
    is_active: bool = True


    @field_validator('level')
    def in_valid_levels(cls, level):
        if level not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            raise ValueError('Not valid level')
        return level

    @field_validator('native_language', 'learned_language')
    def in_valid_languages(cls, language):
        if language not in settings.VALID_LANGUAGES:
            raise ValueError('Not valid language')
        return language

    def to_mongo(self, **kwargs):
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_unset = exclude_unset,
            by_alias = by_alias,
            **kwargs,
        )

        if "_id" not in parsed and 'id' in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        return parsed

    def save(self):

        # client = connect_to_mongodb()
        # client.admin.command('ping')
        # if client:
            # save_data_to_mongodb(client, settings.MONGODB_DATABASE, 'users', self.to_mongo())
        save_data_to_mongodb(settings.MONGODB_DATABASE, 'users', self.to_mongo())
            # close_mongodb_connection(client)

