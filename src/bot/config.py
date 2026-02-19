from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str = "mysql+aiomysql://dogwalker:dogwalker@mysql:3306/dogwalker"
    allowed_users: list[int] = []
    webapp_url: str = ""
    display_timezone: str = "Europe/Moscow"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
