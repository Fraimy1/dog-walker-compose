from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str = "mysql+aiomysql://dogwalker:dogwalker@mysql:3306/dogwalker"
    allowed_users: list[int] = []

    model_config = {"env_file": ".env"}


settings = Settings()
