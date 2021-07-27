import json

from .route import (
    Route,
    Split,
    FILE_PATH,
    ROUTE,
    TITLE,
    CATEGORY,
    INITIAL_STAR,
    TIMING,
    STAR_COUNT,
    VERSION,
    FADEOUT,
    FADEIN,
    XCAM,
    SPLITS,
    SPLIT_TYPE,
    ICON
)

from .constants import (
    SPLIT_NORMAL,
    SPLIT_FADE_ONLY,
    TIMING_RTA,
    TIMING_UP_RTA,
    TIMING_FILE_SELECT
)


def load(file_path):
    try:
        with open(file_path) as route_data:
            data = route_data.read()
            new_data = data[:1] + '"file_path": ' + '"' + file_path + '",' + data[1:]
            decoded_route = RouteDecoder().decode(new_data)
            return decoded_route
    except FileNotFoundError:
        return None


def save(route_data, file):
    with open(file, "w") as write_file:
        json.dump(route_data, write_file, indent=4, cls=RouteEncoder)


class RouteDecoder(json.JSONDecoder):
    def __init__(self, *args, **kargs):
        super().__init__(object_hook=RouteDecoder.route_hook, *args, **kargs)

    @staticmethod
    def route_hook(data):
        if ROUTE not in data:
            return data

        if data[ROUTE]:

            if CATEGORY not in data:
                data[CATEGORY] = ""

            splits = []
            for split_dict in data[SPLITS]:
                # TODO: Separated to keep backwards compatibility with v0.1.x routes. Remove this in next version.
                try:
                    xcam = split_dict[XCAM]
                except KeyError:
                    xcam = -1

                splits.append(Split(split_dict[TITLE],
                                    split_dict[STAR_COUNT],
                                    split_dict[FADEOUT],
                                    split_dict[FADEIN],
                                    xcam,
                                    split_dict[SPLIT_TYPE],
                                    split_dict[ICON]))

            # TODO: Separated to keep backwards compatibility with v0.1.x routes. Remove this in next version.
            try:
                timing = data[TIMING]
            except KeyError:
                timing = TIMING_RTA

            route = Route(data[FILE_PATH],
                          data[TITLE],
                          splits,
                          data[INITIAL_STAR],
                          data[VERSION],
                          data[CATEGORY],
                          timing)

            return route
        else:
            return data


class RouteEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Route):
            splits = []
            for split in o.splits:
                splits.append({TITLE: split.title,
                               STAR_COUNT: split.star_count,
                               FADEOUT: split.on_fadeout,
                               FADEIN: split.on_fadein,
                               XCAM: split.on_xcam,
                               SPLIT_TYPE: split.split_type,
                               ICON: split.icon_path})

            return {ROUTE: True,
                    TITLE: o.title,
                    CATEGORY: o.category,
                    INITIAL_STAR: o.initial_star,
                    VERSION: o.version,
                    TIMING: o.timing,
                    SPLITS: splits}
        else:
            super().default(self, o)


def validate_route(route):
    if route.length < 1:
        return "Route must contain at least one split."

    if route.initial_star < 0 or route.initial_star > 120:
        return "Invalid initial star."

    if route.timing not in (TIMING_RTA, TIMING_UP_RTA, TIMING_FILE_SELECT):
        return "Invalid timing method."

    prev_star_count = -1

    for split in route.splits:
        # Check Split Title
        if type(split.title) != str:
            return "Invalid split title."

        if route.initial_star > split.star_count != -1:
            return "Initial star must be lower than first split star."

        # Check split star
        if type(split.star_count) != int:
            return "Split Star is not a valid integer"

        if split.split_type != SPLIT_FADE_ONLY:
            if split.star_count < 0 or split.star_count > 120:
                return "Split: {} - Invalid Split Star.".format(split.title)
            if split.star_count < prev_star_count:
                return "Split: {} - Split star must be greater than previous split.".format(split.title)

        prev_star_count = split.star_count

        # Check fadeout/in
        if type(split.on_fadeout) != int or split.on_fadeout < 0:
            if split.split_type == SPLIT_NORMAL:
                return "Split: {} - Fadeout count is not a valid integer.".format(split.title)

        if type(split.on_fadein) != int or split.on_fadein < 0:
            if split.split_type == SPLIT_NORMAL:
                return "Split: {} - Fadein count is not a valid integer.".format(split.title)

        if split.on_fadein == 0 and split.on_fadeout == 0:
            if split.split_type == SPLIT_NORMAL:
                return "Split: {} - Fadein and Fadeout are both set to zero.".format(split.title)

        # Check icon path
        if type(split.icon_path) != str and split.icon_path is not None:
            return "Split: {} - Invalid icon_path".format(split.title)

    return None
