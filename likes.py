from app import IMAGES_DIR, connection, render_template, request, session, os, time

def submit_like():
    request_data = request.form
    photoid = request_data["photoid"]
    query = "insert into liked (username, photoID) VALUES (%s, %s)"
    with connection.cursor() as cursor:
            cursor.execute(query, (session["username"], photoid))
