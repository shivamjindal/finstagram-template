from app import IMAGES_DIR, connection, render_template, request, session, os, time

def submit_comment():
    request_data = request.form
    comment = request_data["comment"]
    photoid = request_data["photoid"]
    query = "insert into comment (username, photoID, commentText) VALUES (%s, %s, %s)"
    with connection.cursor() as cursor:
        cursor.execute(query, (session["username"], photoid, comment))

