import rsa306b

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def gaussian(x, a=1, mu=0, sigma=1):
    return a * np.exp(-(x - mu)**2 / (2*sigma**2))

_,_,_,r,f = rsa306b.getIQData()

rsa306b.end()

plt.plot(f,r)
p0 = [100, 5390,1 ]
param, cov = curve_fit(gaussian, f, r, p0=p0)
print(param)
plt.plot(f, gaussian(f,*param))



plt.show()