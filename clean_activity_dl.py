import os
activities_dir = """C:/Users/ryand/Golden Cheetah Dir/dl_activities"""

dl_files = []
for file in os.scandir(activities_dir):
    # add in only files with extension. No dirs
    if "." in file.name:
        dl_files.append(file.name)
    
for file in dl_files:
    if '.fit' not in file:
        os.remove(activities_dir+ "/" + file)

### Ensure muted are not in the active dir
muted_dir = """C:/Users/ryand/Golden Cheetah Dir/dl_activities/muted_activities"""

mute_files = []
for file in os.scandir(muted_dir):
    # add in only files with extension. No dirs
    if "." in file.path:
        mute_files.append(file.name)

for file in dl_files:
    if file in mute_files:
        print(file)
        os.remove(activities_dir + '/' + file)