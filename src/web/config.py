from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql+aiomysql://dogwalker:dogwalker@mysql:3306/dogwalker"
    bot_token: str = ""
    allowed_users: list[int] = []

    model_config = {"env_file": ".env"}


settings = Settings()
