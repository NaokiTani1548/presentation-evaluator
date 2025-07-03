from pydantic import BaseModel, Field


class UserBase(BaseModel):

    user_id: int = Field(..., description="ユーザーID", example=1)

    user_name: str = Field(..., description="ユーザー名", example="山田太郎")

    email_address: str = Field(
        ..., description="メールアドレス", example="taro@example.com"
    )

    password: str = Field(..., description="パスワード", example="password123")
