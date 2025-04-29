def form_span_index(trace, span):
    span_num = len(trace.span_dict)
    span_idx = trace.index_map[span.span_id]
    return str(span_num) + str(span_idx)


def calculate_utility(span_duration, span_idx, utility_dict):
    median, mad = utility_dict[span_idx]
    if mad == 0:
        return 0
    utility = (span_duration - median) / mad
    return utility


# from AutoScope.spanselection.utils.mathUtil import SlidingWindowZScore
# window = SlidingWindowZScore(window_size=100)
# for new_duration in durations:
#     window.update(new_duration)
#     median, mad = window.get_statistics()
#     z_score = (new_duration - median) / mad
#     print(f"Z-score: {z_score}")
