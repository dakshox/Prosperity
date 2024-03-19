import csv
import os

path = r"C:\SandBox\Prosperity\tutorial-round\daksh-work\results-03-19-01"  # Use a raw string
os.chdir(path)
print(os.getcwd())

log_file_path = 'tutorial.log'
output_files = {'Sandbox logs:': 'sandbox.log', 'Activities log:': 'activity.log', 'Trade History:': 'tradehistory.log'}

# Open file handles after changing the directory
file_handles = {key: open(value, 'w') for key, value in output_files.items()}
count = 0

try:
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            line_stripped = line.strip()
            if line_stripped == "Sandbox logs:":
                count = 1
                continue  # Skip writing the header line itself
            elif line_stripped == "Activities log:":
                count = 2
                continue  # Skip writing the header line itself
            elif line_stripped == "Trade History:":
                count = 3
                continue  # Skip writing the header line itself

            if count == 1:
                file_handles['Sandbox logs:'].write(line)
            elif count == 2:
                file_handles['Activities log:'].write(line)
            elif count == 3:
                file_handles['Trade History:'].write(line)
finally:
    # Close all file handles
    for handle in file_handles.values():
        handle.close()

# Specify the path to your log file
log_file_path = 'activity.log'  # The path of your .log file
csv_file_path = 'activity.csv'  # The output CSV file

# Open the log file for reading and the CSV file for writing
with open(log_file_path, 'r') as log_file, open(csv_file_path, 'w', newline='') as csv_file:
    # Create a csv.writer object. Here we specify the delimiter as a comma
    csv_writer = csv.writer(csv_file, delimiter=',')

    # Read each line from the log file
    for line in log_file:
        # Split the line into fields using semicolon as the delimiter
        fields = line.strip().split(';')

        # Write the fields to the CSV file
        csv_writer.writerow(fields)

# Once the conversion is done and the files are closed, delete the log file
os.remove(log_file_path)

# After running this, 'converted_file.csv' will contain the data from your .log file in CSV format,
# and the original '.log' file will be deleted.

print('Done')