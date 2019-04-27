from app import IMAGES_DIR, connection, render_template, request, session, os, time

def submit_like():
    request_data = request.form # get the proper form
    photoid = request_data["photoid"] # get the photoid of the liked photo
    query = "insert into liked (username, photoID) VALUES (%s, %s)" # prepare the query
    with connection.cursor() as cursor:
            cursor.execute(query, (session["username"], photoid)) # submit the photo
