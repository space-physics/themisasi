#!/usr/bin/env python
"""
Using data from ICX249AL datasheet
and Jackel 2014
"""
import pandas
import numpy as np
from matplotlib.pyplot import figure, show

camfn = 'data/icx249al_response.csv'
filtfn = 'data/ir_filter.csv'

resp = pandas.read_csv(camfn, index_col=0)
filt = pandas.read_csv(filtfn, index_col=0)

wl = np.arange(400, 1000, 10)

# %% plot
ax = figure().gca()

resp.plot(ax=ax)
filt.plot(ax=ax)

ax.grid(True)
ax.set_title('THEMIS GBO ASI spectral response')
ax.set_xlabel('wavelength [nm]')
ax.set_ylabel('normalized')

show()
