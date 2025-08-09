import tdtc
import pprint
import csv

# code_data = tdtc.coverage_tdt("47100")  # Example postal code

# pprint.pprint(code_data[0])

# Define the postal code ranges for each province in Castilla y León
province_codes = {
    "Ávila": ["05000", "05999"],
    "Burgos": ["09000", "09999"],
    "León": ["24000", "24999"],
    "Palencia": ["34000", "34999"],
    "Salamanca": ["37000", "37999"],
    "Segovia": ["40000", "40999"],
    "Soria": ["42000", "42999"],
    "Valladolid": ["47000", "47999"],
    "Zamora": ["49000", "49999"]
}

all_data = []

for province, code_range in province_codes.items():
    province_data = tdtc.get_all_coverage_data(output_file="cyl/cyl.txt", 
                                               progress_file="cyl/pg.txt", 
                                               start=int(code_range[0]), 
                                               end=int(code_range[1]))

# Save the data to a CSV file
# with open("castilla_y_leon_tv_coverage.csv", "w", newline='', encoding="utf-8") as csvfile:
#     if all_data:
#         writer = csv.DictWriter(csvfile, fieldnames=all_data[0].keys())
#         writer.writeheader()
#         writer.writerows(all_data)