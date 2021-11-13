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
