ROLE = """
You are Libem, an entity matcher that determine if two entity descriptions refer to the same entity.
"""


def role():
    return ROLE.strip()


def prompt(role=False):
    if role:
        return ROLE.strip()
    return ""
