import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib3
import requests
from requests_ntlm import HttpNtlmAuth
import re
import random
from tqdm import tqdm
from datetime import datetime
from sanitize_filename import sanitize


TQDM_COLORS = [
    "#ff0000",
    "#00ff00",
    "#0000ff",
    "#ffff00",
    "#00ffff",
    "#ff00ff",
    "#ffffff",
    "#000000",
]


download_path = "downloads"
url_cms = "https://cms.guc.edu.eg"
session = requests.Session()

if(not os.path.exists('.env')):
	print("[ERROR] no .env file found")
	exit()

with open('.env', 'r') as f:
	# Setup the authentication for session
	lines = f.readlines()
	username = lines[0].strip()
	password = lines[1].strip()
	if(username == "" or password == ""):
		print("[ERROR] no username or password found")
		exit()
	session.auth = HttpNtlmAuth(username, password)
	session.headers.update({"User-Agent": "Mozilla/5.0"})
	get_args = { "auth": session.auth, "verify": False, }
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def testlogin():
	response = session.get(url_cms)
	if response.status_code != 200:
		print("[ERROR] Authentication failed")
		exit()
	print("[INFO] Authentication successful")

# testlogin()

def download_file(url, path):
	response = session.get(url, stream=True, allow_redirects=True)
	if response.status_code != 200:
		raise Exception("expected 200 status code, found ",response.status_code)
		
	total_size = int(response.headers.get("Content-Length"))

	with open(path, "wb") as f:
		with tqdm(
			total=total_size,
			unit="B",
			unit_scale=True,
			desc=path,
			initial=0,
			dynamic_ncols=True,
			colour=random.choice(TQDM_COLORS),
		) as t:
			for chunk in response.iter_content(chunk_size=1024):
				f.write(chunk)
				t.update(len(chunk))


# TODO:
# bs = BeautifulSoup(session.get(url_cms).text, "html.parser")
# course_links = [link.get("href") for link in bs.find_all("a") if link.get("href")]
# course_links = [ url_cms + link for link in course_links if re.match(r"\/apps\/student\/CourseViewStn\?id(.*)", link) ]

# rgx_get_course_name = re.compile(r"\n*[\(][\|]([^\|]*)[\|][\)]([^\(]*)[\(].*\n*")
# _courses_table = list(
# 	bs.find(
# 		"table",
# 		{"id": "ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses"},
# 	)
# )
# course_names = [ re.sub( rgx_get_course_name, r"\1-\2", _courses_table[i].text.strip(),).strip() for i in range(2, len(_courses_table) - 1) ]

# HARDCORDED TODO:
course_names = ['CSEN901- Artificial Intelligence', 'CSEN903- Advanced Computer lab', 'CSEN909- Human Computer Interaction', 'DMET901- Computer Vision', 'CSEN1095- Data Engineering']
course_links = ['https://cms.guc.edu.eg/apps/student/CourseViewStn?id=572&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=573&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=795&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=571&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=2390&sid=58']

course_names = ['CSEN903- Advanced Computer lab']
course_links = [ 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=573&sid=58']

# bs = BeautifulSoup(session.get(url_cms).text, "html.parser")
files_to_download = []
for (index, course_link) in enumerate(course_links):
	# TODO:
	# course_soup = BeautifulSoup( session.get(course_link).text, "html.parser",)

	course_soup = BeautifulSoup( open("course.html").read(), "html.parser",)
	files_body = course_soup.find_all(class_="card-body" )
	for item in files_body:
		# check if the card is not a course content, useful for `Filter weeks` card
		if item.find('strong') is None:
			continue
		# files_to_download.append(item)

		url = url_cms + item.find("a")["href"]

		week = item.parent.parent.parent.parent.find("h2").text.strip()
		week = re.sub(r"Week: (.*)", "\\1", week)
		week = datetime.strptime(week, "%Y-%m-%d").strftime("W %m-%d")

		rgx_get_file = re.compile(r"[0-9]* - (.*)")
		description = re.sub(rgx_get_file, "\\1", item.find("div").text).strip()

		name = re.sub(rgx_get_file, "\\1", item.find("strong").text).strip()
		name = sanitize(name)

		extension = url.rsplit(".", 1)[1]
		course_path = os.path.join(download_path, course_names[index])
		dir_path = os.path.join(course_path, week)
		path = os.path.join(dir_path, f"{name}.{extension}")

		rated = item.select("input[class='ratedata']")[0]["data-rate"] != "0"

		if(rated): continue

		file_info = {
				"course": course_names[index],
				"week": week,
				"description": description,
				"name": name,
				"extension": extension,
				"path": path,	
				"url": url,
			}

		print(f"course: {course_names[index]}")
		print(f"week: {week}")
		print(f"description: {description}")
		print(f"name: {name}")
		print(f"extension: {extension}")
		print(f"path: {path}")
		print(f"url: {url}")
		# print(file_info)
		print("========")

		files_to_download.append(
			file_info
		)


	# print(files_to_download)
	exit()



