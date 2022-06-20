def calculate_ratio(window_size, region):
    return [region[0] / window_size[0],
            region[1] / window_size[1],
            region[2] / window_size[0],
            region[3] / window_size[1]]
    
    
print(calculate_ratio([617, 454], [0, 0, 617, 454]))