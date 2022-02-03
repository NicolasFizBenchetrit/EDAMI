
# find the starting index of a sub array
def find_sub_array_index(array, sub_array):
    for i in range(0,len(array) - len(sub_array)):
        sub_array_found = True
        z = 0
        while z < len(sub_array) and sub_array_found == True:
            if sub_array[z] != array[i+z]:
                sub_array_found = False
            z += 1
        if sub_array_found:
            return i
    return None
