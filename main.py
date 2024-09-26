import requests

from bs4 import BeautifulSoup

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

# completed_colleges: list[str] = all_colleges # [] 

re_all_colleges: str = "|".join(all_colleges)

from dataclasses import dataclass
from functools import lru_cache
import re, os, sys, pickle, json

# Prevents error due to lots of courses when saving pickle
sys.setrecursionlimit(10000)

from colorama import Fore

from typing import Any, Tuple, Union, Callable

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
        return None
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

      return None

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

    return self.webpage.find(id='course-content').p.text

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

class BUCourseBranch():

  def __init__(self):

    # self.AllCourses: dict[str, Course] = {} course_dir instead

    self.colleges = [BUColleges(col) for col in all_colleges]

    print(self.colleges)

  def run(self) -> None:

    for college in self.colleges:

      college.getCourses()

    return f"{Fore.GREEN}SUCSESS{Fore.WHITE}"

  def __repr__(self) -> str:
    return self.run()

  def __str__(self) -> str:
    return self.__repr__()

class BUColleges():

  def __init__(self, college_name: str) -> None:

    self.name: str = college_name

    pass

  def getCollegeWebpage(self, i: int) -> list[Course]:

    self.college_url = f"https://www.bu.edu/academics/{self.name}/courses/{i if i > 0 else ''}"

    self.webpage = BeautifulSoup(requests.get(self.college_url).text, 'html.parser')

    return self.webpage

  def getCourses(self) -> list[Course]:

    for i in range(1000): # So no infinite loops

      if i % 10 == 0:

        saveCourses(i)

      course_blurbs = [c for c in self.getCollegeWebpage(i).find(class_="course-feed").find_all('li') if c.find('strong') is not None] # and c.find('strong').replace(" ", "").__len__() == 8 ?

      if not course_blurbs: # empty list
        print(f"{Fore.RED}Found No Courses: Last Page {i}{Fore.WHITE}")
        break

      print(f"{Fore.CYAN}Searching {self.name} Page {i}{Fore.WHITE}")

      for index, blurb in enumerate(course_blurbs):

        print(f"{index+1}/{len(course_blurbs)}", end="\r")

        link: str = blurb.find('a')["href"]

        name: str = blurb.find('strong').text.split(":")[0]

        if name in course_dir:

          pass

        else:

          course_dir[name] = Course(name, link=link)

  def __repr__(self) -> str:

    return self.name

  def __str__(self) -> str:

    return self.__repr__()


# Load dict if available
def load_dict() -> None:

  global course_dir

  if os.path.exists(f"{read_file}.pkl") and course_dir is None:
    with open(f"{read_file}.pkl", 'rb') as f:

      print(f"{Fore.LIGHTGREEN_EX}Loading {read_file}.pkl{Fore.WHITE}")

      course_dir = pickle.load(f)

  elif course_dir is not None:

    print(f"{Fore.LIGHTYELLOW_EX}Found existing dict{Fore.WHITE}")

    pass

  else:

    print(f"{Fore.LIGHTRED_EX}No file or dict found, setting to empty dict{Fore.WHITE}")

    course_dir = {}

def saveCourses(i: int) -> None:
    
    global last_save_len

    global num_saves
    
    len_dict: int = len(course_dir)
      
    if len_dict > last_save_len:
    
      print(f"{Fore.MAGENTA}Saving Dict: {len_dict} Courses{Fore.WHITE}")

      with open(f"{save_file}{num_saves}.pkl", 'wb') as file:
          pickle.dump(course_dir, file)
    
      num_saves+=1
      last_save_len = len_dict

      if i % 100 == 0:

        with open(f"saves/{save_file}_{len_dict}.pkl", 'wb') as file:
          pickle.dump(course_dir, file)

      print(f"{Fore.LIGHTGREEN_EX}Save Sucsessful!{Fore.WHITE}")  

    else:

      print(f"{Fore.YELLOW}Not saving dict, no changes detected{Fore.WHITE}")


if __name__ == "__main__":

  course_dir: Union[None, dict[str, Course]] = None

  read_file: str = "courses_directory" # "courses_directory"
  save_file: str = "saves/courses_directory_new"

  load_dict()

  last_save_len: int = len(course_dir)
  num_saves: int = 0

  print(len(course_dir))
  save_branch = BUCourseBranch()
  print(save_branch)