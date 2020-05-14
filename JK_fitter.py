#!/usr/bin/python3
import sys
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import scipy.linalg as la

JKCONFIG = sys.argv[1]
DF_JKCONFIG = pd.read_csv(JKCONFIG,
                          names=["J", "K", "CONFIG"],
                          dtype={
                              "J": int,
                              "K": int,
                              "CONFIG": str
                          })
print("JKCONFIG Loaded")
ENERGY_DATA = sys.argv[2]
DF_ENERGY_DATA = pd.read_csv(ENERGY_DATA,
                             delim_whitespace=True,
                             names=["Filename", "Energy (VASP)"])
FILENAMES = DF_ENERGY_DATA["Filename"].to_numpy()
UIDS = [int(name.split("_")[1]) for name in FILENAMES]
DF_ENERGY_DATA['UIDS'] = UIDS

CONFIGS = DF_JKCONFIG["CONFIG"].to_numpy()
CONFIG_IDS = np.zeros_like(CONFIGS)
for index, config in enumerate(CONFIGS):
    for i, charac in enumerate(config):
        CONFIG_IDS[index] += int(charac) * len(set(list(config)))**i
DF_JKCONFIG['UIDS'] = CONFIG_IDS
J_LIST = np.zeros_like(DF_ENERGY_DATA['UIDS'])
K_LIST = np.zeros_like(DF_ENERGY_DATA['UIDS'])
for index, uid in enumerate(DF_ENERGY_DATA['UIDS']):
    JK_LIST = DF_JKCONFIG['UIDS'].to_numpy()
    index_in_jkconfig = np.nonzero(JK_LIST == uid)[0][0]
    J_LIST[index] = DF_JKCONFIG.at[index_in_jkconfig, 'J']
    K_LIST[index] = DF_JKCONFIG.at[index_in_jkconfig, 'K']
DF_ENERGY_DATA['J'] = J_LIST
DF_ENERGY_DATA['K'] = K_LIST
DATA = np.array([
    list([x, y, z])
    for x, y, z in zip(DF_ENERGY_DATA["J"], DF_ENERGY_DATA["K"],
                       DF_ENERGY_DATA["Energy (VASP)"])
])

X, Y = np.meshgrid(
    np.arange(DF_ENERGY_DATA["J"].min() - 5, DF_ENERGY_DATA["J"].max() + 5,
              0.5),
    np.arange(DF_ENERGY_DATA["K"].min() - 5, DF_ENERGY_DATA["K"].max() + 5,
              0.5),
)
XX = X.flatten()
YY = Y.flatten()

A = np.c_[DATA[:, 0], DATA[:, 1], np.ones(DATA.shape[0])]
C, _, _, _ = la.lstsq(A, DATA[:, 2])
Z = C[0] * X + C[1] * Y + C[2]

FIG = go.Figure(
    data=[
        go.Surface(z=Z, x=X, y=Y, opacity=0.7),
        go.Scatter3d(
            z=DATA[:, 2],
            x=DATA[:, 0],
            y=DATA[:, 1],
            mode="markers",
            marker_color="black",
        ),
    ],
    layout_scene_xaxis_title="J",
    layout_scene_yaxis_title="K",
    layout_scene_zaxis_title="Energy",
    layout_title_text="Fit for 4 Species: J/K = {}".format(C[0] / C[1]),
)
FIG.show()
TITLE = "Parity Plot for 4 Species J-K Model:<br>J = {:.2E}, K = {:.2E}".format(
    C[0], C[1])
DF_ENERGY_DATA["Energy (Model)"] = DF_ENERGY_DATA["J"].to_numpy(
) * C[0] + DF_ENERGY_DATA["K"].to_numpy() * C[1] + C[2]
FIG2 = px.scatter(DF_ENERGY_DATA,
                  x="Energy (Model)",
                  y="Energy (VASP)",
                  title=TITLE,
                  template="presentation")
FIG2.update_traces(
    marker=dict(size=12, line_width=2, line_color="DarkSlateGrey"))
# FIG2.add_shape(type='line', x0=-5.6, y0=-5.6, x1=-6, y1=-6,
#               line_dash='dot', line_width=3)
FIG2.update_layout(width=600, height=600)
FIG2.show()
print(C[0])
print(C[1])
print(C[2])
