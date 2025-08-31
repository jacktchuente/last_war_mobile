from typing_extensions import TypedDict


class AllianceCenterSurvivorOption(TypedDict):
    help_count: int
    mn_reduced: int


def remaining_duration(initial_duration, help_count, mn_reduced, alliance_buff_perc):
    duration = initial_duration
    for _ in range(help_count):
        duration -= mn_reduced
        if duration <= 0:
            return 0
        reduction_sup = max(1, alliance_buff_perc * duration)
        duration -= reduction_sup
        if duration <= 0:
            return 0
    return duration


def find_best_survivor_set_threshold(
        options: tuple[AllianceCenterSurvivorOption, AllianceCenterSurvivorOption],
        max_test=1_000_000,
        alliance_buff_perc=0.005
):
    for d in range(1, max_test + 1):
        duration1 = remaining_duration(d, options[0]['help_count'], options[0]['mn_reduced'], alliance_buff_perc)
        duration2 = remaining_duration(d, options[1]['help_count'], options[1]['mn_reduced'], alliance_buff_perc)
        if duration2 < duration1:
            return d / (60 * 24)
    return None
