from .errors import NotFoundError


class UserService:
    def __init__(self, user_repository):
        self.users = user_repository

    def get_user(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    def list_directory(self, limit=100, offset=0):
        limit = max(1, min(int(limit), 100))
        offset = max(0, int(offset))
        return self.users.list_directory(limit=limit, offset=offset)
