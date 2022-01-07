import os
activities_dir = """C:/Users/ryand/Golden Cheetah Dir/dl_activities"""
# activities_dir = """C:/Users/ryand/Golden Cheetah Dir/dl_activities"""


for dir_,dirs,files in  os.walk(activities_dir):
	for file in files:
		if '.fit' not in file:
			if dir_ != '.':
				os.remove(dir_ + "/" + file)
			else:
				os.remove(activities_dir + "/" + file)

### Ensure muted are not in the active dir
activity_dir_files = files

muted_dir =

for dir_,dirs,files in os.walk(muted_dir):
	for file in files:
		if file not in activity_dir_files:
			print(file)
import time
time.sleep(60)