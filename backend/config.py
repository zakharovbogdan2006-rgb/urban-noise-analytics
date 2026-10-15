from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://noise:change-me@localhost:5432/noise_monitor"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "noise/+/metrics"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
