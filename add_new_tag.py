from app import IMAGES_DIR, connection, render_template, request, session, os, time
import tools
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
			query2 = 'SELECT Photo.photoID FROM  Photo, Belong, Share Where belong.username = %s and belong.groupOwner = share.groupOwner AND Belong.groupName = share.groupName AND photo.photoID = share.photoID UNION (SELECT Photo.photoID FROM Photo, Follow  WHERE (photoOwner = %s ) or (followerUsername = %s AND photoOwner = followeeUsername AND acceptedfollow = TRUE))'			
			with connection.cursor() as cursor:
				cursor.execute(query2, (tagged_name, tagged_name, tagged_name))
			vPhoto = cursor.fetchall()
			isVisible= 0 #true/false to determine if the person can view the photo
			
			for photo in vPhoto:
				currentPhoto = int(photo['photoID'])
				intID = int(photoID)
				if(currentPhoto == intID):
					isVisible= 1
					with connection.cursor() as cursor:
						cursor.execute(query, (tagged_name, photoID, 0))
			if(isVisible == 0):
				#        error = "Friend group with name : %s already exist" % (groupName)
				error = "You cannot tag: %s to this picture because they cannot see the photo" % (tagged_name)
				return render_template('images.html', error=error)



	return render_template('images.html')

