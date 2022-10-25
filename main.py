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
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm_multi_thread_factory import TqdmMultiThreadFactory
import time
import logging
from requests.adapters import HTTPAdapter, Retry
from printer import Printer
import sys


# CLI Arguments
# only supported single argument --no-download(-nd) --no-rate(-nr)
cliarg_no_downlaod = False
cliarg_no_rate = False
if(len(sys.argv) > 1):
	if(sys.argv[1] in ["--no-download", "-nd"]):
		print("[WARN] No Download flag enabled")
		cliarg_no_downlaod = True
	elif(sys.argv[1] in ["--no-rate", "-nr"]):
		print("[WARN] No Rate flag enabled")
		cliarg_no_rate = True

download_path = "downloads"
url_cms = "https://cms.guc.edu.eg"
session = requests.Session()
max_thread_count = 5


printer = Printer()

# logging.basicConfig(level=logging.DEBUG)
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
session.mount('https://', HTTPAdapter(max_retries=retries))

start_time = time.time()
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

def download_file(position, file_info):
	save_path = file_info["path"]
	friendly_name = f"{file_info['course']} ({file_info['name']})" 
	name_ext = file_info["name"]+"."+file_info["extension"]

	if(os.path.exists(save_path)):
		print(f"[WARN] Ignoring File ({name_ext}) already exists in {save_path}")
		return

	response = session.get(file_info['url'], stream=True, allow_redirects=True)
	if response.status_code != 200:
		print("expected 200 status code, found ",response.status_code , response.text)
		raise Exception("expected 200 status code, found ",response.status_code, response.text)
		
	total_size = int(response.headers.get("Content-Length"))

	os.makedirs(os.path.dirname(save_path), exist_ok=True)
	
	with open(save_path, "wb") as f:
		with multi_thread_factory.create(position, friendly_name, total_size) as progress:
			for chunk in response.iter_content(chunk_size=1024):
				f.write(chunk)
				progress.update(len(chunk))

		# with tqdm(
		# 	total=total_size,
		# 	unit="B",
		# 	unit_scale=True,
		# 	desc=friendly_name,
		# 	initial=0,
		# 	dynamic_ncols=True,
		# 	colour=random.choice(TQDM_COLORS),
		# ) as t:
		# 	for chunk in response.iter_content(chunk_size=1024):
		# 		f.write(chunk)
		# 		t.update(len(chunk))

	# Rate the downloaded file
	if(cliarg_no_rate):
		return

	data = {
		"studentid": student_id,
		"videoid": file_info["rateId"],
		"rateid": "5"
	}
	r = session.post("https://cms.guc.edu.eg/apps/student/CourseViewStn.aspx/Goajax2", json=data, )
	if r.status_code != 200:
		print(f"[ERROR] Failed to rate file {name_ext} from {file_info['course']} status code {r.status_code}\n{r.text}", )



bs = BeautifulSoup(session.get(url_cms).text, "html.parser")
course_links = [link.get("href") for link in bs.find_all("a") if link.get("href")]
course_links = [ url_cms + link for link in course_links if re.match(r"\/apps\/student\/CourseViewStn\?id(.*)", link) ]
student_id = bs.select("input[id='ContentPlaceHolderright_ContentPlaceHoldercontent_HiddenFielduser']")[0].get("value")
# bs.select("input[id='HiddenFieldstaffid']")[0].get("value") named this way in each course page

rgx_get_course_name = re.compile(r"\n*[\(][\|]([^\|]*)[\|][\)]([^\(]*)[\(].*\n*")
_courses_table = list(
	bs.find(
		"table",
		{"id": "ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses"},
	)
)
course_names = [ re.sub( rgx_get_course_name, r"\1-\2", _courses_table[i].text.strip(),).strip() for i in range(2, len(_courses_table) - 1) ]

# HARDCODE
# course_names = ['CSEN901- Artificial Intelligence', 'CSEN903- Advanced Computer lab', 'CSEN909- Human Computer Interaction', 'DMET901- Computer Vision', 'CSEN1095- Data Engineering']
# course_links = ['https://cms.guc.edu.eg/apps/student/CourseViewStn?id=572&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=573&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=795&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=571&sid=58', 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=2390&sid=58']

# course_names = ['CSEN903- Advanced Computer lab']
# course_links = [ 'https://cms.guc.edu.eg/apps/student/CourseViewStn?id=573&sid=58']

files_to_download = []
for (index, course_link) in enumerate(course_links):
	course_soup = BeautifulSoup( session.get(course_link).text, "html.parser",)
	# HARDCODE
	# course_soup = BeautifulSoup( open("course.html").read(), "html.parser",)

	course_item = course_soup.find_all(class_="card-body" )
	for item in course_item:
		# check if the card is not a course content, useful for `Filter weeks` card
		if item.find('strong') is None:
			continue
		

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
		# dir_path = os.path.join(course_path, week)
		# path = os.path.join(dir_path, f"{name}.{extension}")
		path = os.path.join(course_path, f"{name}.{extension}")

		# Print needed files, this before rate to keep course name when displayed
		printer.addKey(course_names[index])
		printer.display()

		rated = item.select("input[class='ratedata']")[0]["data-rate"] != "0"
		if(rated): continue
		rateId = item.select("input[class='ratedata']")[0]['data-id']


		printer.addValue(course_names[index], name, description)

		file_info = {
				"course": course_names[index],
				"week": week,
				"description": description,
				"name": name,
				"extension": extension,
				"path": path,	
				"url": url,
				"rateId": rateId
			}

		# print(f"course: {course_names[index]}")
		# print(f"week: {week}")
		# print(f"description: {description}")
		# print(f"name: {name}")
		# print(f"extension: {extension}")
		# print(f"path: {path}")
		# print(f"url: {url}")
		# print(file_info)
		# print("========")


		files_to_download.append(
			file_info
		)






# threads = []
# for file_info in files_to_download:
# 	thread = threading.Thread(target=download_file, args=(file_info,))
# 	thread.start()
# 	threads.append(thread)

if(not cliarg_no_downlaod):
	with ThreadPoolExecutor(max_workers=max_thread_count) as executor:
		multi_thread_factory = TqdmMultiThreadFactory()
		for i, file_info in enumerate(files_to_download, 1):
			executor.submit(download_file, i, file_info)

if(len(files_to_download) == 0):
	print("[INFO] No unrated files to download")
print("Done in", int(time.time() - start_time), "seconds")