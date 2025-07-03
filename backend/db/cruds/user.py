# sqlalchemy
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# pydantic
from pydantic import ValidationError

# schemas
from ..schemas.user import UserBase as UserSchema

# models
from ..models.user import User as UserModel


# ユーザー作成
async def post_user(
    db_session: AsyncSession, user_name: str, email_address: str, password: str
) -> UserSchema:
    try:
        # UserSchema から UserModel(DB用クラス) へ変換
        db_user = UserModel(
            user_name=user_name,
            email_address=email_address,
            password=password,
        )

        db_session.add(db_user)
        await db_session.commit()

        return UserSchema(
            user_id=db_user.user_id,
            user_name=db_user.user_name,
            email_address=db_user.email_address,
            password=db_user.password,
        )

    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}")
    except ValidationError as e:
        raise Exception(f"Data validation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


# user_idを元にユーザー取得
async def get_user_by_user_id(
    db_session: AsyncSession, user_id: int
) -> UserSchema | None:

    try:
        result = await db_session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        db_user = result.scalar_one_or_none()
        if db_user is None:
            return None

        user = UserSchema(
            user_id=db_user.user_id,
            user_name=db_user.user_name,
            email_address=db_user.email_address,
            password=db_user.password,
        )
        return user

    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}")
    except ValidationError as e:
        raise Exception(f"Data validation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


# ユーザー一覧
async def get_all_users(db_session: AsyncSession) -> list[UserSchema]:
    try:
        result = await db_session.execute(select(UserModel))
        db_users = result.scalars().all()
        return [
            UserSchema(
                user_id=user.user_id,
                user_name=user.user_name,
                email_address=user.email_address,
                password=user.password,
            )
            for user in db_users
        ]
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}")
    except ValidationError as e:
        raise Exception(f"Data validation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")
