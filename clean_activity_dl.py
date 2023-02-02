import os
activities_dir = """C:/Users/ryand/Golden Cheetah Dir/dl_activities"""

dl_files = []
max_ctime = 0
for file in os.scandir(activities_dir):
    # add in only files with extension. No dirs
    if "." in file.name:
        dl_files.append(file)
    if os.path.getctime(file.path) > max_ctime:
        max_ctime = os.path.getctime(file.path)

ctime_lookback = 60*4
min_ctime = max_ctime - ctime_lookback


# for file in dl_files:
#     if '.fit' not in file.name:
#         os.remove(file.path)
#     elif os.path.getctime(file.path) <  min_ctime:
#         os.remove(file.path)

### Ensure muted are not in the active dir
muted_dir = """C:/Users/ryand/Golden Cheetah Dir/dl_activities/muted_activities"""
old_dir = """C:/Users/ryand/Golden Cheetah Dir/dl_activities/older_activities"""

## Gather file lists from old and muted folders
mute_files = []
for file in os.scandir(muted_dir):
    # add in only files with extension. No dirs
    if "." in file.path:
        mute_files.append(file.name)
old_files = []
for file in os.scandir(old_dir):
    # add in only files with extension. No dirs
    if "." in file.path:
        old_files.append(file.name)


for file in dl_files:
    if '.fit' not in file.name:
        ## Remove non .fit files. Don't need em
        os.remove(file.path)

    if (file.name in mute_files) or (file.name in old_files):
        ## Delete files that have already been moved to mute and old dirs
        os.remove(file.path)

    elif os.path.getctime(file.path) <  min_ctime:
        ## Move files that have not been moved to mute and old dirs
        os.rename(file.path, '/'.join(old_dir,file.name))