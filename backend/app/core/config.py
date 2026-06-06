# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str

    # 新增安全設定
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 告訴 Pydantic 從 .env 檔案讀取變數
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 創建 settings 物件，供其他檔案引入使用
settings = Settings()
