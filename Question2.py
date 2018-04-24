import numpy as np
from sympy import *

#part 1
all_cause_mortality=18/1000
stroke_mortality=36.2/100000
non_stroke_mortality=all_cause_mortality-stroke_mortality
stroke_deathrate=-np.log(1 - stroke_mortality)
non_stroke_deathrate=-np.log(1-non_stroke_mortality)
print(stroke_deathrate,non_stroke_deathrate)

#part2
first_stroke=15/1000
rate_firststroke=-np.log(1-first_stroke)
print(rate_firststroke)

#part3
lambda1=rate_firststroke*0.9
lambda2=rate_firststroke*0.1
print(lambda1,lambda2)

#part4
annual_recurrent=0.17
rate_recurrent=-np.log(1-annual_recurrent)
print(rate_recurrent)

#part5
rate_poststr_stroke=rate_recurrent*0.8
rate_poststr_strokedeath=rate_recurrent*0.2
print(rate_poststr_stroke,rate_poststr_strokedeath)

#part6
time_stroke=7/365
rate_stroke_post=1/time_stroke
print(rate_stroke_post)

rate_poststr_stroke_withtherapy=rate_poststr_stroke*(1-0.25)
therapy_non_stroke_deathrate=non_stroke_deathrate*(1+0.05)
