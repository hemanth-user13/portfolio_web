from .models import *

DATA =[
  "Bolgum Hemanth Goud",
  "Jr. Developer",
  "Omnics Technologies Pvt. Ltd.",
  "React with TypeScript",
  "Django REST Framework",
  "Started career in June 2024",
  "Worked on RGC Manager (lawyer application)",
  "Worked on other internal projects",
  "B.Tech in Computer Science Engineering",
  "GITAM University, Hyderabad",
  "9 CGPA"
]


def run():
    for d in DATA:
        MyData.objects.create(text=d)

    print("Portfolio data inserted!")
