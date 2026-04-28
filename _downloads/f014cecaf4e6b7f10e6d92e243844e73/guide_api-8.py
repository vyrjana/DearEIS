from deareis import (
  PlotSeries,
  PlotSettings,
  PlotType,
  Project,
  mpl,
)
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import (
  Optional,
  Tuple,
)
figure, axis = plt.subplots()
axes = [axis]
project: Project = Project.from_file("../../tests/example-project-v6.json")
plot: PlotSettings = [plot for plot in project.get_plots() if plot.get_label() == "Noisy"][0]
assert plot.get_type() == PlotType.NYQUIST_IMPEDANCE
series: PlotSeries
for series in project.get_plot_series(plot):
  label: Optional[str] = None
  if series.has_legend():
    label = series.get_label()
  color: Tuple[float, float, float, float] = series.get_color()
  marker: Optional[str] = mpl.MPL_MARKERS.get(series.get_marker())
  if series.has_line():
    _ = mpl.plot_nyquist(
      series,
      colors={"impedance": color},
      markers={"impedance": marker},
      line=True,
      label=label if marker is None else "",
      figure=figure,
      axes=axes,
      num_per_decade=50,
    )
    if marker is not None:
      _ = mpl.plot_nyquist(
        series,
        colors={"impedance": color},
        markers={"impedance": marker},
        line=False,
        label=label,
        figure=figure,
        axes=axes,
        num_per_decade=-1,
      )
  elif marker is not None:
    _ = mpl.plot_nyquist(
      series,
      colors={"impedance": color},
      markers={"impedance": marker},
      line=False,
      label=label,
      figure=figure,
      axes=axes,
      num_per_decade=-1,
    )
_ = figure.suptitle(plot.get_label())
_ = axis.legend()