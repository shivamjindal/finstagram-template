from app import IMAGES_DIR, connection, render_template, request, session, os, time
import tools

def get_user_tag_requests():
    result = None
    query = "select photoid, filepath from photo natural join tag where username = %s and acceptedTag !=True"
    with connection.cursor() as cursor:
        cursor.execute(query, session["username"])
        result = cursor.fetchall()
    return result

def submit_tag_action():
    request_data = request.form
    response = request_data["response"]
    photoid = request_data["photoid"]
    if response == "accept":
        query = "update tag set acceptedTag = 1 where photoid = %s and username = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (photoid, session["username"]))
    elif response == "decline":
        query = "delete from tag where photoid = %s and username = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (photoid, session["username"]))

