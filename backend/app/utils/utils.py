from app.models.user import User


def check_rights(cur_user: User, tar_user: User):
    return cur_user.id == tar_user.id or cur_user.is_admin