import plotly.graph_objects as go


def default_plotly_template() -> go.layout.Template:
    """Returns the default Plotly template stylized to the Epistemix color scheme.

    Parameters
    ----------
    none

    Returns
    -------
    plotly.graph_objs.layout._template.Template
        A Plotly template object

    Notes
    -----
    - It is not quite clear as to why `go.layout.Template` returns a
      `plotly.graph_objs.layout._template.Template` object, though it probably
      has something to do with some internal inheritence structures going on
      the plotly library. Plotly's documentation is poor and searching for
      `go.layout.Template` proved to be fruitless.
    """
    return go.layout.Template(
        {
            "data": {
                "bar": [
                    {
                        "error_x": {"color": "#f2f5fa"},
                        "error_y": {"color": "#f2f5fa"},
                        "marker": {
                            "line": {"color": "#000533", "width": 0.5},
                            "pattern": {
                                "fillmode": "overlay",
                                "size": 10,
                                "solidity": 0.2,
                            },
                        },
                        "type": "bar",
                    }
                ],
                "barpolar": [
                    {
                        "marker": {
                            "line": {"color": "#000533", "width": 0.5},
                            "pattern": {
                                "fillmode": "overlay",
                                "size": 10,
                                "solidity": 0.2,
                            },
                        },
                        "type": "barpolar",
                    }
                ],
                "carpet": [
                    {
                        "aaxis": {
                            "endlinecolor": "#B0B9E4",
                            "gridcolor": "#6C76A8",
                            "linecolor": "#6C76A8",
                            "minorgridcolor": "#6C76A8",
                            "startlinecolor": "#B0B9E4",
                        },
                        "baxis": {
                            "endlinecolor": "#B0B9E4",
                            "gridcolor": "#6C76A8",
                            "linecolor": "#6C76A8",
                            "minorgridcolor": "#6C76A8",
                            "startlinecolor": "#B0B9E4",
                        },
                        "type": "carpet",
                    }
                ],
                "choropleth": [
                    {"colorbar": {"outlinewidth": 0, "ticks": ""}, "type": "choropleth"}
                ],
                "contour": [
                    {
                        "colorbar": {"outlinewidth": 0, "ticks": ""},
                        "colorscale": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "type": "contour",
                    }
                ],
                "contourcarpet": [
                    {
                        "colorbar": {"outlinewidth": 0, "ticks": ""},
                        "type": "contourcarpet",
                    }
                ],
                "heatmap": [
                    {
                        "colorbar": {"outlinewidth": 0, "ticks": ""},
                        "colorscale": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "type": "heatmap",
                    }
                ],
                "heatmapgl": [
                    {
                        "colorbar": {"outlinewidth": 0, "ticks": ""},
                        "colorscale": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "type": "heatmapgl",
                    }
                ],
                "histogram": [
                    {
                        "marker": {
                            "pattern": {
                                "fillmode": "overlay",
                                "size": 10,
                                "solidity": 0.2,
                            }
                        },
                        "type": "histogram",
                    }
                ],
                "histogram2d": [
                    {
                        "colorbar": {"outlinewidth": 0, "ticks": ""},
                        "colorscale": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "type": "histogram2d",
                    }
                ],
                "histogram2dcontour": [
                    {
                        "colorbar": {"outlinewidth": 0, "ticks": ""},
                        "colorscale": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "type": "histogram2dcontour",
                    }
                ],
                "mesh3d": [
                    {"colorbar": {"outlinewidth": 0, "ticks": ""}, "type": "mesh3d"}
                ],
                "parcoords": [
                    {
                        "line": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "parcoords",
                    }
                ],
                "pie": [{"automargin": True, "type": "pie"}],
                "scatter": [
                    {"marker": {"line": {"color": "#4D5685"}}, "type": "scatter"}
                ],
                "scatter3d": [
                    {
                        "line": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "scatter3d",
                    }
                ],
                "scattercarpet": [
                    {
                        "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "scattercarpet",
                    }
                ],
                "scattergeo": [
                    {
                        "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "scattergeo",
                    }
                ],
                "scattergl": [
                    {"marker": {"line": {"color": "#4D5685"}}, "type": "scattergl"}
                ],
                "scattermapbox": [
                    {
                        "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "scattermapbox",
                    }
                ],
                "scatterpolar": [
                    {
                        "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "scatterpolar",
                    }
                ],
                "scatterpolargl": [
                    {
                        "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "scatterpolargl",
                    }
                ],
                "scatterternary": [
                    {
                        "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        "type": "scatterternary",
                    }
                ],
                "surface": [
                    {
                        "colorbar": {"outlinewidth": 0, "ticks": ""},
                        "colorscale": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "type": "surface",
                    }
                ],
                "table": [
                    {
                        "cells": {
                            "fill": {"color": "#6C76A8"},
                            "line": {"color": "#000533"},
                        },
                        "header": {
                            "fill": {"color": "#2a3f5f"},
                            "line": {"color": "#000533"},
                        },
                        "type": "table",
                    }
                ],
            },
            "layout": {
                "annotationdefaults": {
                    "arrowcolor": "#f2f5fa",
                    "arrowhead": 0,
                    "arrowwidth": 1,
                },
                "autotypenumbers": "strict",
                "coloraxis": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                "colorscale": {
                    "diverging": [
                        [0, "#8e0152"],
                        [0.1, "#c51b7d"],
                        [0.2, "#de77ae"],
                        [0.3, "#f1b6da"],
                        [0.4, "#fde0ef"],
                        [0.5, "#f7f7f7"],
                        [0.6, "#e6f5d0"],
                        [0.7, "#b8e186"],
                        [0.8, "#7fbc41"],
                        [0.9, "#4d9221"],
                        [1, "#276419"],
                    ],
                    "sequential": [
                        [0.0, "#0d0887"],
                        [0.1111111111111111, "#46039f"],
                        [0.2222222222222222, "#7201a8"],
                        [0.3333333333333333, "#9c179e"],
                        [0.4444444444444444, "#bd3786"],
                        [0.5555555555555556, "#d8576b"],
                        [0.6666666666666666, "#ed7953"],
                        [0.7777777777777778, "#fb9f3a"],
                        [0.8888888888888888, "#fdca26"],
                        [1.0, "#f0f921"],
                    ],
                    "sequentialminus": [
                        [0.0, "#0d0887"],
                        [0.1111111111111111, "#46039f"],
                        [0.2222222222222222, "#7201a8"],
                        [0.3333333333333333, "#9c179e"],
                        [0.4444444444444444, "#bd3786"],
                        [0.5555555555555556, "#d8576b"],
                        [0.6666666666666666, "#ed7953"],
                        [0.7777777777777778, "#fb9f3a"],
                        [0.8888888888888888, "#fdca26"],
                        [1.0, "#f0f921"],
                    ],
                },
                "colorway": [
                    "#636efa",
                    "#EF553B",
                    "#00cc96",
                    "#ab63fa",
                    "#FFA15A",
                    "#19d3f3",
                    "#FF6692",
                    "#B6E880",
                    "#FF97FF",
                    "#FECB52",
                ],
                "font": {"color": "#D2D8F7", "family": "Epistemix Label"},
                "geo": {
                    "bgcolor": "#000533",
                    "lakecolor": "#000533",
                    "landcolor": "#000533",
                    "showlakes": True,
                    "showland": True,
                    "subunitcolor": "#6C76A8",
                },
                "hoverlabel": {"align": "left"},
                "hovermode": "closest",
                "mapbox": {"style": "dark"},
                "paper_bgcolor": "#000533",
                "plot_bgcolor": "#000533",
                "polar": {
                    "angularaxis": {
                        "gridcolor": "#6C76A8",
                        "linecolor": "#6C76A8",
                        "ticks": "",
                    },
                    "bgcolor": "#000533",
                    "radialaxis": {
                        "gridcolor": "#6C76A8",
                        "linecolor": "#6C76A8",
                        "ticks": "",
                    },
                },
                "scene": {
                    "xaxis": {
                        "backgroundcolor": "#000533",
                        "gridcolor": "#6C76A8",
                        "gridwidth": 2,
                        "linecolor": "#6C76A8",
                        "showbackground": True,
                        "ticks": "",
                        "zerolinecolor": "#B0B9E4",
                    },
                    "yaxis": {
                        "backgroundcolor": "#000533",
                        "gridcolor": "#6C76A8",
                        "gridwidth": 2,
                        "linecolor": "#6C76A8",
                        "showbackground": True,
                        "ticks": "",
                        "zerolinecolor": "#B0B9E4",
                    },
                    "zaxis": {
                        "backgroundcolor": "#000533",
                        "gridcolor": "#6C76A8",
                        "gridwidth": 2,
                        "linecolor": "#6C76A8",
                        "showbackground": True,
                        "ticks": "",
                        "zerolinecolor": "#B0B9E4",
                    },
                },
                "shapedefaults": {"line": {"color": "#f2f5fa"}},
                "sliderdefaults": {
                    "bgcolor": "#B0B9E4",
                    "bordercolor": "#000533",
                    "borderwidth": 1,
                    "tickwidth": 0,
                },
                "ternary": {
                    "aaxis": {
                        "gridcolor": "#6C76A8",
                        "linecolor": "#6C76A8",
                        "ticks": "",
                    },
                    "baxis": {
                        "gridcolor": "#6C76A8",
                        "linecolor": "#6C76A8",
                        "ticks": "",
                    },
                    "bgcolor": "#000533",
                    "caxis": {
                        "gridcolor": "#6C76A8",
                        "linecolor": "#6C76A8",
                        "ticks": "",
                    },
                },
                "title": {"font": {"family": "Epistemix Headline"}, "x": 0.05},
                "updatemenudefaults": {"bgcolor": "#6C76A8", "borderwidth": 0},
                "xaxis": {
                    "automargin": True,
                    "gridcolor": "#4D5685",
                    "linecolor": "#6C76A8",
                    "ticks": "",
                    "title": {"standoff": 15},
                    "zerolinecolor": "#4D5685",
                    "zerolinewidth": 2,
                },
                "yaxis": {
                    "automargin": True,
                    "gridcolor": "#4D5685",
                    "linecolor": "#6C76A8",
                    "ticks": "",
                    "title": {"standoff": 15},
                    "zerolinecolor": "#4D5685",
                    "zerolinewidth": 2,
                },
            },
        }
    )