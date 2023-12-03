class ResultWhat:
    __slots__ = ('name', )
    name: str

    def __init__(self, name: str):
        s = super()
        s.__setattr__('name', name)

    def __repr__(self):
        return self.name

    def __setattr__(self, key, value):
        raise TypeError(f"{type(self).__name__} object is immutable!")

    def __delattr__(self, item):
        raise TypeError(f"{type(self).__name__} object is immutable!")


class WHAT:
    class USER:
        user = ResultWhat("user")
        user_id = ResultWhat("user_id")
        login = ResultWhat("login")
        full_name = ResultWhat("full_name")
        password = ResultWhat("password")
        password_confirm = ResultWhat("password_confirm")

    class PASSFILE:
        passfile_id = ResultWhat("passfile_id")
        version = ResultWhat("version")
        name = ResultWhat("name")
        color = ResultWhat("color")
        created_on = ResultWhat("created_on")

    class HISTORY:
        kind = ResultWhat("kind")
