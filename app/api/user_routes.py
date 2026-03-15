from fastapi import APIRouter
from app.models.user_model import UserCreate, UserUpdate
from app.services.user_service import (
    create_user,
    get_users,
    update_user,
    delete_user
)

router = APIRouter()


@router.post("/users")
def create_user_route(user: UserCreate):
    return create_user(user.name, user.email)


@router.get("/users")
def get_users_route():
    return get_users()


@router.put("/users/{user_id}")
def update_user_route(user_id: str, user: UserUpdate):
    return update_user(user_id, user.name, user.email)


@router.delete("/users/{user_id}")
def delete_user_route(user_id: str):
    return delete_user(user_id)
