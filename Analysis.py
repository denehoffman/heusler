#!/usr/bin/python3
"""This file contains all the end-user plotting code for analyzing the Heusler
energy minimizations"""
import argparse
import numpy as np
import plotly.graph_objects as go
import pandas as pd


def genPlot(XYZ, configuration, colors=["blue", "red", "green", "purple"]):
    """Creates the set of plots needed to display a
    single crystal configuration"""
    num_lines = 0
    with open(XYZ) as file:
        num_lines = sum(1 for _ in file)
    basis = np.genfromtxt(XYZ, skip_footer=num_lines - 3)
    basis_coords = np.genfromtxt(XYZ, skip_header=4, usecols=(0, 1, 2))
    species = np.genfromtxt(XYZ, skip_header=4, usecols=(3))
    coords = basis_coords.dot(basis)

    basis_shifts = []
    plot_list = []
    #    for i in [-1, 0, 1]:
    #        for j in [-1, 0, 1]:
    #            for k in [-1, 0, 1]:
    #                basis_shifts.append([i, j, k])
    basis_shifts.append([0, 0, 0])
    basis_shifts = np.array(basis_shifts)
    shifts = basis_shifts.dot(basis)
    for shift in shifts:
        shifted_coords = np.array([list(coord + shift) for coord in coords])
        for i in range(len(species)):
            plot_list.append(
                go.Scatter3d(
                    x=[shifted_coords[i, 0]],
                    y=[shifted_coords[i, 1]],
                    z=[shifted_coords[i, 2]],
                    mode="markers",
                    marker=dict(size=9, color=colors[configuration[i]]),
                )
            )
    return plot_list


def draw(XYZ, configuration, title, colors=["blue", "red", "green", "purple"]):
    plot_list = genPlot(XYZ, configuration, colors)
    layout = go.Layout(
        title=title,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(projection=dict(type="orthographic")),
        ),
    )
    fig = go.Figure(data=plot_list, layout=layout)
    fig.show()


def getName(uid, num_species):
    if num_species == 2:
        if uid == 59:
            return "CsCl (59)"
        if uid == 58:
            return "NaTl (58)"
    if num_species == 3:
        if uid == 1:
            return "IH (1)"
        if uid == 1601:
            return "FH: (1601)"
    if num_species == 4:
        if uid == 2296:
            return "QH: (2296)"
    return "Unknown Species > {}".format(uid)


def drawHeatmap(XYZ, csv):
    species = np.genfromtxt(XYZ, skip_header=4, usecols=(3))
    num_species = len(set(species))
    ids = pd.read_csv(csv, header=None).to_numpy()[:, :-1]
    vals = np.linspace(-1, 1, np.shape(ids)[0])
    layout = go.Layout(
        title="{}-Species Diagonalized Phase Diagram".format(num_species),
        width=700,
        height=700,
        font=dict(family="Courier New, monospace", size=18, color="#000000"),
        xaxis_title="K (next-nearest-neighbor interaction strength)",
        yaxis_title="J (nearest-neighbor interaction strength)",
    )
    hovertext_array = np.empty_like(ids, dtype=object)
    hovertext_array[:] = "Other"
    for uid in set(ids.flatten()):
        hovertext_array[np.where(ids == uid)] = getName(uid, num_species)
    fig = go.Figure(
        data=go.Heatmap(
            z=ids ** 2 * (-1) ** ids,
            x=vals,
            y=vals,
            colorscale=[[0, "#800020"], [1, "#208000"]],
            showscale=False,
            text=hovertext_array,
            hovertemplate="<b>Crystal Type: %{text}</b><br><br>"
            + "Nearest-Neighbor Interaction Strength: %{y}<br>"
            + "Next-Nearest-Neighbor Interaction Strength: %{x}<br>"
            + "<extra></extra>",
        ),
        layout=layout,
    )
    fig.show()


def drawRadial(XYZ, csv):
    species = np.genfromtxt(XYZ, skip_header=4, usecols=(3))
    num_species = len(set(species))
    jkid = pd.read_csv(csv, header=None, names=["J", "K", "THETA", "ID"])
    idlist = list(set(jkid["ID"]))
    ids_scaled = np.zeros(len(jkid.index))
    for index, identifier in enumerate(jkid["ID"]):
        ids_scaled[index] = idlist.index(identifier)
    jkid["ID_Scaled"] = ids_scaled
    _, n_unique_jk = np.unique(jkid["THETA"], return_counts=True)
    rvals = []
    jkid["Width_deg"] = np.ones(len(jkid.index)) * 360 / len(n_unique_jk)
    for index, count in enumerate(n_unique_jk):
        rvals = np.append(rvals, np.ones(count) / count)
    jkid["R"] = rvals
    jkid.drop(jkid.tail(1).index, inplace=True)
    fig = go.Figure(
        go.Barpolar(
            theta=jkid["THETA"] * 180 / np.pi,
            r=jkid["R"],
            marker_color=jkid["ID_Scaled"],
            marker_line_width=0,
            width=jkid["Width_deg"],
            hovertext=[
                "J: {:4.10f}, K: {:4.10f}, ID: {}".format(
                    jkid["J"].to_numpy()[i],
                    jkid["K"].to_numpy()[i],
                    getName(jkid["ID"].to_numpy()[i], num_species),
                )
                for i in range(len(jkid.index))
            ],
        )
    )
    fig.update_layout(
        title="Radial J-K Plot of {}".format(csv.split("/")[-1]),
        bargap=0.0,
        barmode="stack",
    )
    fig.show()


def drawByUID(XYZ, enum, uid):
    species = np.genfromtxt(XYZ, skip_header=4, usecols=(3))
    num_species = len(set(species))
    start = 1
    with open(enum) as file:
        while not file.readline().startswith("start"):
            start += 1
    enum_arr = np.genfromtxt(enum, skip_header=start, usecols=(26), dtype=str)
    config = np.array(list(enum_arr[uid - 1]), dtype=int)
    draw(XYZ, config, getName(uid, num_species))


def main():
    parser = argparse.ArgumentParser(
        description="Analysis Suite for Simple Interaction Hamiltonians",
        epilog="Written by Nathaniel D. Hoffman",
    )
    parser.add_argument("XYZ", help="XYZ File")
    parser.add_argument("ENUM", help="Output of enum.x")
    parser.add_argument("--map", help="Map a CSV of Energies")
    parser.add_argument("--rad", help="Draw Map from Radial Data")
    parser.add_argument("--draw", help="Draw by enum.x ID", type=int)
    args = parser.parse_args()
    if args.draw is not None:
        drawByUID(args.XYZ, args.ENUM, args.draw)
    if args.map is not None:
        drawHeatmap(args.XYZ, args.map)
    if args.rad is not None:
        drawRadial(args.XYZ, args.rad)


if __name__ == "__main__":
    main()
