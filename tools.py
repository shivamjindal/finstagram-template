from app import connection, session


def _get_current_user_groups():
    query = "SELECT groupName, groupOwner FROM Belong WHERE username = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, session["username"])
    data = cursor.fetchall()
    return data