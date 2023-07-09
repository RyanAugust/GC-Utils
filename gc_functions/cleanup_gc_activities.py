import os

import_dir = '/Users/ryanduecker/Dropbox/GoldenCheetah/Ryan Duecker/imports'

### Gather files
for a,b,c in os.walk(import_dir):
    break

### First sort
keep_files = []
dump_files = []

for file in c:
    if " 2.fit" in file.lower():
        dump_files.append(file)
    else:
        keep_files.append(file)

lower_keep_files = []
for file in keep_files:
    lower_keep_files.append(file.lower())

### Approve delete list based on name and size
delete_files = []

for file in dump_files:
    new_name = file.lower().replace(' 2.fit','.fit')
    original_dup_path = import_dir + '/' + file
    original_dup_size = os.path.getsize(original_dup_path)
    
    for keep_file in keep_files:
        if new_name == keep_file.lower():
            keep_file_size = os.path.getsize(import_dir + '/' + keep_file)
            if original_dup_size==keep_file_size:
                delete_files.append(file)

### Perform Delete 
for file in delete_files:
    os.remove(import_dir + '/' + file)