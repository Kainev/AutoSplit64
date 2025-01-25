# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

def point_from_ratio_2d(size: list, point_ratio: list) -> list:
    return [
        int(round(size[0] * point_ratio[0])),
        int(round(size[1] * point_ratio[1]))
    ]