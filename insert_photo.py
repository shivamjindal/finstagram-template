from app import IMAGES_DIR, connection, render_template, request, session, os, time


def upload_image():
    if request.files:
        image_file = request.files.get("imageToUpload", "")
        all_followers = int(request.form.get("allFollowers") != None)
        caption = request.form.get("caption")
        image_name = image_file.filename
        filepath = os.path.join(IMAGES_DIR, image_name)
        image_file.save(filepath)

        query = "INSERT INTO photo (photoOwner, timestamp, filePath, allFollowers, caption) VALUES (%s, %s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (session["username"], time.strftime('%Y-%m-%d %H:%M:%S'), image_name, all_followers, caption))
            photo_id = cursor.lastrowid
            print("1234 EXEC", cursor._executed, "\nRESULT", photo_id)


        # if not all_followers:
        #     query = "INSERT INTO Share (groupName, groupOwner, photoID) VALUES (%s, %s, %s)"
        #     with connection.cursor() as cursor:
        #         cursor.execute(query, ())

        message = "Image has been successfully uploaded."
        return render_template("upload.html", message=message)
    else:
        message = "Failed to upload image."
        return render_template("upload.html", message=message)