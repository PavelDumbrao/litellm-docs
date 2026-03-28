from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Prodamus payment gateway
    PRODAMUS_SECRET_KEY: str
    PRODAMUS_BASE_URL: str = "https://proaicommunity.payform.ru/"

    # LiteLLM API
    LITELLM_API_URL: str = "http://litellm:4000"
    LITELLM_MASTER_KEY: str

    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Operator internal
    OPERATOR_SECRET: str = ""

    # Pricing
    FIXED_RUB_PER_CREDIT: float = 85.0

    # Loyalty program
    LOYALTY_THRESHOLD_RUB: float = 50000.0
    LOYALTY_DISCOUNT_PERCENT: float = 5.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
