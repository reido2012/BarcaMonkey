import string
from concurrent import futures


def do_concurrently(a_function, a_list, max_workers=20):
    workers = min(max_workers, len(a_list))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(a_function, a_list)

    return res

def format_horse_name(horse_name):
    translator = str.maketrans('', '', string.punctuation)
    horse_name = horse_name.lower().replace(" ", "")
    horse_name.translate(translator)
    return horse_name


