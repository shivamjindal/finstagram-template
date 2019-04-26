from app import IMAGES_DIR, connection, render_template, request, session, os, time
import tools
<<<<<<< .merge_file_KW2gVK
# -*- coding: utf-8 -*-
def new_tag():
    if request.form:
        requestData = request.form
        tagged_name = requestData["username"]
        photoID = requestData["photoID"]
        user = session["username"]
        print(user + " tagged " + tagged_name + " in photoID: " + photoID)
        query = "INSERT into Tag (username, photoID, acceptedTag) VALUES (%s, %s, %s)"
        #if the user is tagging themselves
        if(user == tagged_name):
        	with connection.cursor() as cursor:
        		cursor.execute(query, (tagged_name, photoID, 1))
        #if they are tagging someone else
        else:
		#if query is visiable to the tagged_name then the result (tagged_name, photoID, 0)
			query2 = 'SELECT Photo.photoID, timestamp, filePath, photoOwner, caption FROM  Photo, Belong, Share Where belong.username = %s and belong.groupOwner = share.groupOwner AND Belong.groupName = share.groupName AND photo.photoID = share.photoID UNION (SELECT Photo.photoID, timestamp, filePath, photoOwner, caption FROM Photo, Follow  WHERE (photoOwner = %s ) or (followerUsername = %s AND photoOwner = followeeUsername AND acceptedfollow = TRUE)) ORDER BY Timestamp DESC'
			with connection.cursor() as cursor:
				cursor.execute(query2, (tagged_name, tagged_name, tagged_name))
			vPhoto = cursor.fetchall()
			isVisible= 0; #true/false to determine if the person can view the photo
			#print(vPhoto)
			for photo in vPhoto:
				#print(photo)
				# print(photo['photoID'])
				currentPhoto = photo['photoID']
				# print("Does the local number above match tag number below")
				# print(photoID)
				if(currentPhoto == photoID):
					print(here)
					isVisible= 1
					with connection.cursor() as cursor:
						cursor.execute(query, (tagged_name, photoID, 0))
			if(isVisible == 0):
				return render_template('home.html')


	return render_template('/images.html')

=======


def new_tag():
    if request.files:
        image_file = request.files.get("imageToUpload", "")
        all_followers = int(request.form.get("allFollowers") != None)
        caption = request.form.get("caption")
        image_name = image_file.filename
        filepath = os.path.join(IMAGES_DIR, image_name)
        image_file.save(filepath)
        photo_id = int(request.form.get("tags") != None)
        person_tagged = request.form.get("Username")

        query = "INSERT INTO tag (username, photoID, acceptedTag) VALUES (%s, %s, %s)"
        with connection.cursor() as cursor:
            #if(session["username"] == the user name of the photo ID)
                #cursor.execute(query, (session["username"], 0, True))
            cursor.execute(query, (session["username"], 0, True))
            photo_id = cursor.lastrowid


        if not all_followers:
            query = "INSERT INTO Share (groupName, groupOwner, photoID) VALUES (%s, %s, %s)"
            groups = request.form.getlist('group')
            for group in groups:
                group_divided_to_list = group.split(",")
                groupName = group_divided_to_list[0]
                groupOwner = group_divided_to_list[1]
                with connection.cursor() as cursor:
                    cursor.execute(query, (groupName, groupOwner, photo_id))

        message = "Tag request has been sent."
        return render_template("upload.html", message=message, user_groups=tools._get_current_user_groups())
    else:
        message = "Failed to upload image."
        return render_template("upload.html", message=message, user_groups=tools._get_current_user_groups())
>>>>>>> .merge_file_fk4BaK
