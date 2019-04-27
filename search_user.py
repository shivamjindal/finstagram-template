from app import IMAGES_DIR, connection, render_template, request, session, os, time
import tools

def search_dir():
	if request.files:
		searcher = session["username"]
		poster = request.form.get("poster")
		query = "SELECT * FROM Photo Where owner = %s"
		with connection.cursor() as cursor:
			cursor.execute(query, (poster))
		data = cursor.fetchall()
	
		return render_template('images.html', images= data)
	else: 
		print("here in search_dir")
		return render_template('search_poster.html')