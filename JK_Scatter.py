#!/usr/bin/python3
import numpy as np
import pandas as pd
import plotly.express as px
import sys

fname = sys.argv[1]
jkdata = pd.read_csv(fname, header=None, names=['J', 'K', 'Config'], dtype={'J':int, 'K':int, 'Config':str})
fig = px.scatter(jkdata, x="J", y="K", hover_data=['Config'])
fig.update_xaxes(dtick=4)
fig.update_yaxes(dtick=4)
fig.show()
grouped = jkdata.groupby(['J', 'K'])
for jk, group in grouped:
    print("{},{},{}".format(jk[0], jk[1], group['Config'].to_numpy()[0]))
