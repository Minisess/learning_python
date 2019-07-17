from random import choice, shuffle
from collections import Sequence, Counter
from multiprocessing.pool import Pool
import json
import gooey

data = None
day_off_flag = False

@gooey.Gooey
def interface():
    """
    ra_data = {"AA": ["mon", "sun", "tue"], "AV": ["sun", "tue"], "DS": ["Sun", "Mon", ], "KJ": ["wed", "thr", "Tue",
    ], "KH": ["Mon", "wed", "Thr", ], "BS": ["Wed", "Thr", "mon", ], "MF": ["wed", "sun", "tue"]}
    total_weeks = 16
    trials = 100
    """  # make data object global for reference

    parser = gooey.GooeyParser()
    parser.add_argument("--ra_data", dest='ra_data', type=str,
                        help="ra data needs to be formatted as a dictionary with each entry being the name or "
                             "initials followed by the days they are available using three letter abbreviations "
                             """ "AA": ["mon", "sun", "tue"], "AV": ["sun", "tue"], ... """
                             "sun, mon, tue, wed, thr, fri, sat")
    parser.add_argument('-w', dest="total_time", type=str, required=False,
                        help="The number of weeks that the scheduler needs to print out",
                        default='4')
    parser.add_argument('-t', dest="trials", type=str, required=False,
                        help="Increase this if you are having trouble getting good results",
                        default='50')
    parser.add_argument('-s', dest="load_save", required=False,
                        help="If you would like to run the same as the last run set to true", type=str,
                        default='False')
    parser.add_argument('--off', dest="day_off", required=False, help="if each person needs a day off set to true",
                        type=str, default=False)

    # convert arguments from strings into their type
    args = parser.parse_args()
    args.ra_data = """ {"AA": ["sat"], "AV": ["sun", "tue"], "DS": ["Sun", "Mon", ]} """
    ra_data = eval(args.ra_data)
    assert type(ra_data) is dict
    weeks = int(args.total_time)
    trials = int(args.trials)
    if args.day_off:
        global day_off_flag
        day_off_flag = True
    if args.load_save.lower() == "true":
        with open('save.json', 'r') as f:
            load_data = json.load(f)  # needs to add additional load logic
            print(load_data)
            return
    # pack information into data object
    main(ra_data, weeks, trials)
    with open('save.json', 'w') as f:
        json.dump(data, f)  # needs to add additional load logic


def initializer(ra_data, weeks, trials):
    global data
    data = Data(ra_data, weeks, trials)


def main(ra_data, weeks, trials):
    with Pool(4, initializer=initializer, initargs=[ra_data, weeks, trials]) as p:
        bests = p.map(permutation_combine, [1, 2, 3, 4])
    best_of_the_best = min(bests, key=lambda x: x[2])
    calender, ras, _ = best_of_the_best
    display_instance = Data(ra_data, weeks, trials)
    display_results(calender, ras, display_instance)


def permutation_combine(*args, **kwargs):
    unavailable_cache = 123
    for _ in range(data.trials):
        # while unavailable_cache > 3:
        try:
            temp_calender, temp_ras, unavailable_num = sort_loop()
            temp_calender = unavailable_x_break_sort(temp_calender, temp_ras)
        except TimeoutError:
            print("Timeout: trying again")
            continue
        if unavailable_num < unavailable_cache:
            unavailable_cache = unavailable_num
            calender = temp_calender
            ras = temp_ras
    return calender, ras, unavailable_cache


def sort_loop():
    ras = create_ras(data.ra_data, data.week_to_day_map)
    # counter determines the period that is being sorted through
    counter = 0
    # this tuple will not change
    calender = create_calender(data.period)
    # counts the number of unavailable weeks in the schedule
    unavailable_num = 0
    # timeout to prevent impossible sorting causes restart
    timeout_counter = 0
    # loops until everyone has had a period off
    while True:
        # tuple is not changed
        current_week = list(ras)
        # list of RAs who have not had a break picks one to have the next period off
        no_break = [ra for ra in ras if not ra.period_off]
        day_off = choice(list(no_break))
        day_off.period_off = True
        if day_off_flag:
            current_week.remove(day_off)
        # check pref one
        for pref in range(3):
            shuffle(current_week)
            for ra in current_week:
                if ra[0] is None:
                    print("All RAs require at least one preferred day")
                    raise IndexError
                # checks if they have a preference for this slot
                if ra[pref] is None:
                    continue
                # checks if they already have a day they are working
                if ra in calender[counter].values():
                    continue
                # checks if preference is used and if not assigns it
                if ra[pref] not in calender[counter]:
                    calender[counter][ra[pref]] = ra
                    ra.total_days += (1 * data.weeks_per_period)
                if timeout_counter > 100:
                    raise TimeoutError
                timeout_counter += 1

        for x in range(7):
            if x not in calender[counter]:
                calender[counter][x] = "Unavailable"
                unavailable_num += 1

        counter += 1
        if counter >= data.period:
            break

    return calender, ras, unavailable_num


##### final sorting methods #####
def unavailable_x_break_sort(calender, ras):
    """Checks to see if any days off can replace unavailable spaces by looking at the whole work period"""
    total_available = []
    for x in calender:
        total_available.extend(list(set(ras) - set(x.values())))
    check = Counter(total_available)
    select_available = (x for x in check.items() if x[1] > 1)
    unavailable_days = ((week, day) for week, _ in enumerate(calender) for day in _ if _[day] == "Unavailable")
    for time in unavailable_days:
        for ra in select_available:
            if time[1] in ra[0]:
                # replace unavailable with them
                calender[time[0]][time[1]] = ra[0]
    return calender


####### creates major objects for manipulation ############
def create_ras(ra_data, map):
    for prefs in ra_data.values():
        for index, day in enumerate(prefs):
            if isinstance(day, str):
                prefs[index] = map[day.lower()]
    test_set = ra_data
    ras = [RA(key, test_set[key]) for key in test_set]
    return tuple(ras)


def create_calender(periods: int) -> list:
    calender = [{} for _ in range(periods)]
    return calender


########## all front end logic ##############
def display_results(calender: list, ras: tuple, display_instance):
    print(f"Period length = about {display_instance.weeks_per_period}")
    render_calender(calender, ras)
    print()
    #print_ra_stats(ras)


def render_calender(calender: list, ras: tuple):
    for num, x in enumerate(calender):
        difference = set(ras) - set(x.values())
        # print(list(zip(x.keys(), x.values())))
        print(f"Period {num + 1} weeks")
        print(f"Sun:{x[0]} | Mon:{x[1]} | Tue:{x[2]} | Wed:{x[3]} | Thur:{x[4]} | Fri:{x[5]} | Sat:{x[6]}     Not Included: {difference}")
        print()

# seems to print with additional days mostly just used for debugging
def print_ra_stats(ras):
    for ra in ras:
        print(f"-----{ra}------")
        print(f"Total days worked: {ra.total_days}")
        print(f"Period off {ra.period_off}")
        print()


class RA(Sequence):
    def __init__(self, name, days):
        self.name = name
        self.pref_day = list(days)
        self.total_days = 0
        self.period_off = False

    def __iter__(self):
        return (x for x in self.pref_day)

    def __len__(self):
        return len(self.pref_day)

    def __getitem__(self, index):
        try:
            return self.pref_day[index]
        except IndexError:
            return None

    def __repr__(self):
        return "<{}>".format(self.name)


class Data:

    def __init__(self, ra_data: dict, total_weeks: int, trials: int):
        self.ra_data = ra_data
        self.total_weeks = total_weeks
        self.trials = trials
        self.period = len(self.ra_data)
        self.weeks_per_period = total_weeks // self.period
        if total_weeks % self.period:
            self.weeks_per_period += 1

    week_to_day_map = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thr": 4, 'fri': 5, 'sat': 6}


if __name__ == "__main__":
    interface()
