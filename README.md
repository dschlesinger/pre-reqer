# pre-reqer
**For finding course info @ BU**
[Download PKL File](https://drive.google.com/file/d/1SWcJW0IXldnk658u8EoOuaJgOAxW6iCP/view?usp=drive_link)

  &darr; in [doc.ipynb](doc.ipynb)
 
## Query Courses

### To load pickle file

```py
from main import Course
import pickle

# Should take around a minute
with open("courses_directory.pkl", "rb") as f:
  course_directory: dict[str, Course] = pickle.load(f)
```
### Find Class

```py
College: str = "CAS" # Three letter acronym like "CAS"
Department: str = "BI" # Two letter acronym like "BI"
Number: int = 203 # Three numbers like "203"

c: Course = course_directory[f"{College} {Department} {Number}"]
```

### Methods

#### Get Course Name, Code, and Attr

```py
College, Department, Number = c.College, c.Department, c.Number

code: str = c.__repr__() # ex. CAS BI 203 

class_name: str = c.getCourseName() # ex. Cell Biology
```

#### Get PreReqs and CoReqs and Attr
```py
pre_pres, co_reqs, leads_to = [c.UndergradReq + c.GradReq, c.UndergradCoReq + c.GradCoReq, c.Post]

# Returns clips with relivant info for course reqs
pre_req_text: dict[str, str] = c.getPreReqsText()

# Returns classes for each category
pre_req_classes: dict[str, list[Course]] = c.getPreReqs()

# Keys reversed
_ = {
        "Graduate Prerequisites:": "gpr",
        "Graduate Corequisite:": "gcr",
        "Undergraduate Prerequisites:": "upr",
        "Undergraduate Corequisites:": "ucr",
        "Prerequisites:": "pr",
        "Corequisites": "cr" 
}
```

#### Hubs

```py
Hubs: list[str] = c.getHubs()
```

#### tmi (to much information)

```py
c.tmi() # returns str
```

#### Webpage and url

```py
from bs4 import BeautifulSoup

website: BeautifulSoup = c.webpage

description: str = c.getDesc() # id='course-content' of course page

url: str = c.url

link: str = c.link # kwarg for c.__init__() for web scraping

valid_link: bool = c.valid_link # False if page not found
```

## Construct Course

```py
# Broken right now, have to declare Course class in same place as course_directory

name: str = "CAS BI 203"

c: Course = Course(name, link=None, cd=course_directory)
```

## Webscraping

Edit all_colleges if I missed one

```py
# Caution does a lot, broken have to declare BUCourseBranch class in same place as course_directory

from main import BUCourseBranch

save_branch = BUCourseBranch()
save_branch.run() # or save_branch.__repr__()
```

Automatically calls saveCourses(i) every 10 pages, savefile every 100 pages