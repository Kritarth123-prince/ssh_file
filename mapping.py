import os
import subprocess
from collections import defaultdict

repo_path = 'DataAnnotation'
output_file = os.path.join(repo_path, 'uploaders.txt')

os.chdir(repo_path)
file_uploaders = defaultdict(list)

result = subprocess.run(['git', 'log', '--pretty=format:%an', '--name-only'], capture_output=True, text=True)

print("Raw output from git log:")
print(result.stdout)

lines = result.stdout.strip().split('\n')
current_author = None

for line in lines:
    if line:
        if not line.startswith(' '):
            current_author = line
        else:
            filename = line.strip()
            if current_author:
                file_uploaders[current_author].append(filename)

if file_uploaders:
    with open(output_file, 'w') as f:
        for author, files in file_uploaders.items():
            f.write(f"{author}\n")
            for file in files:
                f.write(f"{file}\n")
            f.write("\n")

    print(f"File uploaders information written to {output_file}")
else:
    print("No uploader information found.")
