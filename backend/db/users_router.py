from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_dbsession

# schemas
from .schemas.user import UserBase

# cruds
from .cruds.user import post_user, get_user_by_user_id, get_all_users as get_all_users_crud

# create router
router = APIRouter(tags=["users"], prefix="/users")


# /sinup
@router.post("/signup")
async def signup(
    user_name: str,
    email_address: str,
    password: str,
    db: AsyncSession = Depends(get_dbsession),
) -> UserBase | None:
    # UserBaseスキーマを使ってユーザー情報を作成
    user = UserBase(
        user_name=user_name,
        email_address=email_address,
        password=password,
    )

    created_user = await post_user(db, user_name, email_address, password)

    return created_user


# /signin
@router.post("/signin")
async def signin(
    user_id: str,
    password: str,
    db: AsyncSession = Depends(get_dbsession),
) -> UserBase | None:

    user: UserBase | None = await get_user_by_user_id(db, int(user_id))
    
    # ユーザーが存在しない場合
    if user is None:
        print("User not found")
        return None

    # パスワードが一致する場合
    if user.password == password:
        return user

    # パスワードが一致しない場合
    else:
        print("Password is incorrect")
        return None
    
# /get_all_users
@router.get("/get_all_users")
async def get_all_users(db: AsyncSession = Depends(get_dbsession)) -> list[UserBase]:
    users = await get_all_users_crud(db)
    return users