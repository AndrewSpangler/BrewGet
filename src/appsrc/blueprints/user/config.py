import os
SQLALCHEMY_BINDS = {
    "user_db": "sqlite:///" + os.path.join(os.getcwd(), "databases/users.sqlite"),
}
ADMIN_NAV_LINKS = {
    "Users":("user.users",{}),
    "Background Tasks":("user.background_tasks",{}),
}
