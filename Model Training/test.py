# import numpy as np

# original_list = np.array([[0.71607774, 0.00811757, 0.16500716, 0.00261414, 0.00229892, 0.10103297, 0.00303211, 0.00181942]])

# # Use argsort to get the indices in descending order
# indices_descending = np.argsort(original_list[0])[::-1]

# # Create a new list with "tech" before each index and "@gmail.com" after
# new_list = ["tech" + str(index) + "@gmail.com" for index in indices_descending]

# print(new_list)

# Sample list of strings
my_list = ["string1", "string2", "value2"]

# Sample dictionary with "id" keys and associated values
my_dict = {"id1": "value1", "id2": "value2", "id3": "value3"}

# Key to compare against
key_to_compare = "id2"

# Check if each string in the list matches the value associated with the key_to_compare
for item in my_list:
    if item == my_dict.get(key_to_compare):
        print(f"'{item}' matches the value associated with key '{key_to_compare}'.")
    else:
        print(f"'{item}' does not match the value associated with key '{key_to_compare}'.")