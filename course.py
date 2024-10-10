from typing import Any, Union, Tuple
from bs4 import BeautifulSoup
from colorama import Fore

import re, requests

college_codes: dict[str, str] = {
    "QST": "questrom"
}

# All Colleges

all_colleges: list[str] = [
    "CAS",
    "COM",
    "ENG",
    "HUB",
    "QST",
    "CDS",
    "SAR",
    "SHA",
    "CGS",
    "CFA"
]

class Course():

  def __init__(self, name: str, link: str = None, cd: dict[str, Any] = None):

    if cd is None:

      global course_dir

    else:

      course_dir = cd

    self.college_codes: dict[str, str] = {
        "QST": "questrom"
    }

    self.link: str = link

    self.College, self.Department, self.Number, self.url, self.webpage = Course.getWebpage(name, link)

    course_dir[self.__repr__()] = self

    self.Post: list[Course] = []

    self.UndergradReq: list[Course] = []

    self.UndergradCoReq: list[Course] = []

    self.GradReq: list[Course] = []

    self.GradCoReq: list[Course] = []

    self.valid_link: bool = True

    if "Page not found" in self.webpage.title.string:

      self.valid_link = False

      print(f"Class {self.__repr__()} not found")

    else:

      pulled_class_rel: dict[str, list[Course]] = self.getPreReqs()

      for key, value in zip(pulled_class_rel.keys(), pulled_class_rel.values()):

        # "Graduate Prerequisites:": "gpr",
        # "Graduate Corequisite:": "gcr",
        # "Undergraduate Prerequisites:": "upr",
        # "Undergraduate Corequisites:": "ucr",
        # "Prerequisites:": "pr",
        # "Corequisites": "cr" 

        match key:

          case 'gpr':

            self.GradReq = value

          case 'gcr':

            self.GradCoReq = value

          case 'upr':

            self.UndergradReq = value

          case 'ucr':

            self.UndergradCoReq = value

          case 'pr':

            self.UndergradReq.extend(value)

          case 'cr':

            self.UndergradCoReq.extend(value)

      for ureq in self.UndergradReq:

        ureq.Post.append(self)

      for greq in self.GradReq:

        greq.Post.append(self)

    self.all_reqs: list[Course] = self.UndergradReq + self.GradReq

    self.all_co_reqs: list[Course] = self.UndergradCoReq + self.GradCoReq

    self.tmi()

  def __str__(self):
    return f"{self.College} {self.Department} {self.Number}"

  def __repr__(self):
    return self.__str__()
  
  def to_dict(self):
    
    return {
      "link": self.link,
      "College": self.College,
      "Department": self.Department,
      "Number": self.Number,
      "url": self.url,
      "webpage": self.webpage,
      "Post": self.Post,
      "UndergradReq": self.UndergradReq,
      "UndergradCoReq": self.UndergradCoReq,
      "GradReq": self.GradReq,
      'GradCoReq': self.GradCoReq,
      'valid_link': self.valid_link,
      'all_reqs': self.all_reqs,
      'all_co_reqs': self.all_co_reqs,
      "Hubs": self.getHubs(),
      "Desc": self.getDesc(),
      "CourseName": self.getCourseName()
   } 
  
  def tmi(self) -> str:

    return f"{self} ({self.getCourseName()}) = R {'No Pre Reqs' if not self.all_reqs else self.all_reqs} C {'No Co Reqs' if not self.all_co_reqs else self.all_co_reqs} {self.getPreReqsText() if self.getPreReqsText() is not None and not self.all_reqs else ''}"

  def getPreReqsText(self) -> dict[str, str]:

    #Check for info box

    info_box = self.webpage.find(id="info-box")

    if info_box is not None and "requisites" in info_box.text:

      page_text = info_box.text

    else:
      #get text through description
      try:
        page_text: str = self.getDesc()
      except AttributeError as ae:
        return {}
      except Exception as e:
        print(self.__repr__())

        raise e

    search: str = r'(?:Graduate Prerequisites:|Undergraduate Prerequisites:|Prerequisites:|Graduate Corequisite:|Undergraduate Corequisites:|Corequisites|\s-\s)'

    map_find_clean: dict[str, str] = {
        "Graduate Prerequisites:": "gpr",
        "Graduate Corequisite:": "gcr",
        "Undergraduate Prerequisites:": "upr",
        "Undergraduate Corequisites:": "ucr",
        "Prerequisites:": "pr",
        "Corequisites": "cr" 
    }

    order: list[str] = re.findall(search, page_text) # Order of splicing

    if len(order) == 0:

      return {}

    elif len(set(order)) != len(order):

      pass # print(f"{Fore.RED}Multiple of the same order found in {self.__repr__()} {order}{Fore.WHITE}")

    found: dict[str, str] = {

    }

    page_text = page_text.split(order[0])[1]

    for i, item in enumerate(order):
        
      if item != " - ":

        try:

          found[map_find_clean[item]] = page_text.split(order[i+1])[0]

          page_text = page_text.split(order[i+1])[1]
      
        except IndexError as ie:
      
          found[map_find_clean[item]] = page_text

          return found

    
    # Should not run

    return found

  def getPreReqs(self) -> list[Any]:

    t: Union[dict[str, str], None] = self.getPreReqsText()

    if t is None:

      return {}

    else:

      return self.scanForCourses(t)

  @staticmethod
  def getCourseNameStatic(webpage: BeautifulSoup) -> str:

    return webpage.find_all('h1')[1].text

  def getCourseName(self) -> str:

    try:
      return self.webpage.find_all('h1')[1].text
    except AttributeError as ae:
      return None

  def getDesc(self) -> str:

    if self.valid_link:

      return self.webpage.find(id='course-content').p.text
    
    else:

      return "Webpage not found"

  def getHubs(self) -> list[str]:

    try:

      return [li.text for li in self.webpage.find('ul', class_="cf-hub-offerings").find_all('li')]

    except:

      return []

  def formatCourses(self, courses: list[str]) -> list[Any]:


    clean_courses: list[str] = []

    last_college: str = "CAS"

    for course in courses:

      rm_space = course.replace(" ", "")

      # ex WR101
      if len(rm_space) == 5:

        lc: str = f"{last_college} {rm_space[slice(0, 2)]} {rm_space[slice(2,5)]}"

        sc: str = f"{self.College} {rm_space[slice(0, 2)]} {rm_space[slice(2,5)]}"

        if "Page not found" not in Course.getWebpage(lc)[-1].title.string:

          clean_courses.append(f"{last_college} {rm_space[slice(0, 2)]} {rm_space[slice(2,5)]}")

        elif "Page not found" not in Course.getWebpage(sc)[-1].title.string:

          # Incase same college infered

          clean_courses.append(f"{self.College} {rm_space[slice(0, 2)]} {rm_space[slice(2,5)]}")

        else:

          print(f"Neither {lc} or {sc} found")

          clean_courses.append(f"{last_college} {rm_space[slice(0, 2)]} {rm_space[slice(2,5)]}?")


      elif len(rm_space) == 8:

        last_college = rm_space[slice(0,3)]

        clean_courses.append(f"{rm_space[slice(0, 3)]} {rm_space[slice(3, 5)]} {rm_space[slice(5,8)]}")

      else:

        raise Exception(f"{rm_space} not a valid course")

    print(f"{self.__repr__()} pre req: {str(clean_courses)}")

    return [Course(c) if c not in course_dir else course_dir[c] for c in clean_courses if not c.endswith("?") and c != self.__repr__()]

  def scanForCourses(self, text: dict[str, str]) -> list[str]:

    search: str = r'(?:CAS|COM|ENG|HUB|QST|CDS|SAR|SHA|CGS|CFA)?\s?[A-Za-z]{2}\s?\d{3}'

    rdict = {}

    for key, value in zip(text.keys(), text.values()):

      rdict[key] = self.formatCourses(re.findall(search, value))

    return rdict

  @staticmethod
  def getWebpage(c: str, link: str = None) -> Tuple[str, str, int, str, BeautifulSoup]:

    College, Department, Number = c.split(" ")

    if link is None:
      url = f"https://www.bu.edu/academics/{College.lower() if College not in college_codes else college_codes[College]}/courses/{College.lower()}-{Department.lower()}-{Number}/"

    else:
      url = f"https://www.bu.edu{link}"

    webpage = BeautifulSoup(requests.get(url).text, 'html.parser')

    return College, Department, Number, url, webpage

  @staticmethod
  def getName(c: str) -> str:

    return Course.getCourseNameStatic(Course.getWebpage(c)[-1])