from app.database.db import users_db
import uuid


def create_user(name: str, email: str):
    user_id = str(uuid.uuid4())

    user = {
        "id": user_id,
        "name": name,
        "email": email
    }

    users_db[user_id] = user

    return user


def get_users():
    return list(users_db.values())


def update_user(user_id: str, name: str = None, email: str = None):

    if user_id not in users_db:
        return {"error": "User not found"}

    if name:
        users_db[user_id]["name"] = name

    if email:
        users_db[user_id]["email"] = email

    return users_db[user_id]


def delete_user(user_id: str):

    if user_id not in users_db:
        return {"error": "User not found"}

    deleted_user = users_db.pop(user_id)

    return deleted_user
