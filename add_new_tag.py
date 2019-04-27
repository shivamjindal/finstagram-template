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
			query2 = 'SELECT Photo.photoID, timestamp, filePath, photoOwner, caption FROM  Photo, Belong, Share Where belong.username = %s and belong.groupOwner = share.groupOwner AND Belong.groupName = share.groupName AND photo.photoID = share.photoID UNION (SELECT Photo.photoID, timestamp, filePath, photoOwner, caption FROM Photo, Follow  WHERE (photoOwner = %s ) or (followerUsername = %s AND photoOwner = followeeUsername AND acceptedfollow = TRUE)) ORDER BY Timestamp DESC'
			with connection.cursor() as cursor:
				cursor.execute(query2, (tagged_name, tagged_name, tagged_name))
			vPhoto = cursor.fetchall()
			isVisible= 0; #true/false to determine if the person can view the photo
			print(vPhoto)
			for photo in vPhoto:
				print(photo)
				print(photo['photoID'])
				currentPhoto = int(photo['photoID'])
				print("Does the local number above match tag number below")
				print(photoID)
				intphoto = int(photoID)
				if(currentPhoto == intphoto):
					print("here")
					isVisible= 1
					with connection.cursor() as cursor:
						cursor.execute(query, (tagged_name, photoID, 0))
			if(isVisible == 0):
				return render_template('home.html')


	return render_template('/images.html')

