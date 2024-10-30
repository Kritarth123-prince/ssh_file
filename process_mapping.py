from collections import defaultdict
import chardet

# Set input and output file paths
input_file = 'mapping2.txt'   # Path to the input text file
output_file = 'mapping1.txt' # Path to the output file

# Detect encoding
with open(input_file, 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']

# Initialize a dictionary to store files by uploader name
file_uploaders = defaultdict(set)  # Using a set to avoid duplicates

# Read the input file and process each line
with open(input_file, 'r', encoding=encoding) as f:
    current_author = None
    for line in f:
        line = line.strip()
        if line:  # Only process non-empty lines
            if '.' in line:  # This line is assumed to be a filename (contains a dot)
                if current_author:  # Ensure we have an author name
                    file_uploaders[current_author].add(line)  # Add file to the set to avoid duplicates
            else:
                # This line is an author name
                current_author = line  # Update the current author name

# Write the grouped and deduplicated output to a new file
with open(output_file, 'w', encoding='utf-8') as f:
    for author, files in file_uploaders.items():
        f.write(f"{author}\n")  # Write the author's name
        for file in sorted(files):  # Sort files alphabetically for readability
            f.write(f"{file}\n")  # Write each associated file
        f.write("\n")  # Add a newline for separation between authors

print(f"Consolidated file uploaders information written to {output_file}")
