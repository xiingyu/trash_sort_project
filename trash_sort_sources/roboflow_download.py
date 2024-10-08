
# from roboflow import Roboflow
# rf = Roboflow(api_key="hhGdvI8f5C6he2aJHkwZ")
# project = rf.workspace("school-kxuuy").project("deneme-nvvno")
# version = project.version(3)
# dataset = version.download("yolov8")
  
# from roboflow import Roboflow
# rf = Roboflow(api_key="SWVwOL6kemDxJolVvqjT")
# project = rf.workspace("embedded-7b0yi").project("trash_sort-t289i")
# version = project.version(1)
# dataset = version.download("yolov8")
                              
                              
#                               !pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="SWVwOL6kemDxJolVvqjT")
project = rf.workspace("embedded-7b0yi").project("trash_sort-t289i")
version = project.version(2)
dataset = version.download("yolov8")
                