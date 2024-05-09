import csv

with open("instance/households.csv") as f:
    reader = csv.DictReader(f)
    households = list(reader)

lines = "Address\n"
for household in households:
    lines += f"{household['Full']}\n"

with open("instance/addresses.txt", "w") as f:
    f.write(lines)
