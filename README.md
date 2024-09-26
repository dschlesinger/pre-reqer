# pre-reqer
**For finding course info @ BU**
[Download PKL File](https://drive.google.com/file/d/1j5x3z0w5zGzo_D1jMjOdnziRhQxyJEY5/view?usp=sharing)

  &darr; in [doc.ipynb](doc.ipynb)
 
## Query Courses

### To load pickle file

<code>from main import Course
import pickle<br>
\# Should take around a minute
with open("courses_directory.pkl", "rb") as f:
&nbsp;&nbsp;&nbsp;&nbsp;course_directory: dict[str, Course] = pickle.load(f)</code>
### Find Class
<code>College: str = "CAS" # Three letter acronym like "CAS"
Department: str = "BI" # Two letter acronym like "BI"
Number: int = 203 # Three numbers like "203"
<br>
c: Course = course_directory[f"{College} {Department} {Number}"]</code>

### Methods

#### Get Course Name, Code, and Attr

<code>College, Department, Number = c.College, c.Department, c.Number
<br>
code: str = c.\_\_repr\_\_() # ex. CAS BI 203 
<br>
class_name: str = c.getCourseName() # ex. Cell Biology</code>

#### Get PreReqs and CoReqs and Attr
<code>pre_pres, co_reqs, leads_to = [c.UndergradReq + c.GradReq, c.UndergradCoReq + c.GradCoReq, c.Post]
<br>
\# Returns clips with relivant info for course reqs
pre_req_text: dict[str, str] = c.getPreReqsText()
<br>
\# Returns classes for each category
pre_req_classes: dict[str, list[Course]] = c.getPreReqs()
<br>
\# Keys reversed
_ = {
        "Graduate Prerequisites:": "gpr",
        "Graduate Corequisite:": "gcr",
        "Undergraduate Prerequisites:": "upr",
        "Undergraduate Corequisites:": "ucr",
        "Prerequisites:": "pr",
        "Corequisites": "cr" 
}</code>

#### Hubs

<code>Hubs: list[str] = c.getHubs()</code>

#### tmi (to much information)

<code>c.tmi() # returns str</code>

#### Webpage and url

<code>from bs4 import BeautifulSoup
<br>
website: BeautifulSoup = c.webpage
<br>
description: str = c.getDesc() # id='course-content' of course page
<br>
url: str = c.url
<br>
link: str = c.link # kwarg for c.\_\_init\_\_() for web scraping
<br>
valid_link: bool = c.valid_link # False if page not found</code>

## Construct Course

<code># Broken right now, have to declare Course class in same place as course_directory
<br>
name: str = "CAS BI 203"
<br>
c: Course = Course(name, link=None, cd=course_directory)</code>

## Webscraping

Edit all_colleges if I missed one

<code># Caution does a lot, broken have to declare BUCourseBranch class in same place as course_directory
<br>
from main import BUCourseBranch
<br>
save_branch = BUCourseBranch()
save_branch.run() # or save_branch.__repr__()</code>

Automatically calls saveCourses(i) every 10 pages, savefile every 100 pages