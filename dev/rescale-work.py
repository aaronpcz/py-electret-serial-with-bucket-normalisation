import time

print(time.time())


# min_allowed = 1
# max_allowed = 100
#
# mic_range_min = 0
# mic_range_max = 1000
#
# def rescale(i_value):
#     return ((max_allowed - min_allowed) * (i_value * mic_range_min) / (mic_range_max - mic_range_min)) + min_allowed
#
# def rescale_1(val):
#     return int(((val - mic_range_min) / (mic_range_max - mic_range_min)) * (max_allowed - min_allowed) + min_allowed)
#
# print(rescale_1(500))
# print(rescale_1(1))
# print(rescale_1(0))
# print(rescale_1(12))
# print(rescale_1(10))
# print(rescale_1(51))
# print(rescale_1(240))