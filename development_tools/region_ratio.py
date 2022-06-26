def calculate_ratio(window_size, region):
    return [region[0] / window_size[0],
            region[1] / window_size[1],
            region[2] / window_size[0],
            region[3] / window_size[1]]
    
    
    
print(calculate_ratio([23, 23], [19, 18, 1, 1]))

# JP Star coordinates
# print(calculate_ratio([618, 452], [516, 7, 92, 49]))