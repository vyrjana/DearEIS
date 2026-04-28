from deareis import Project
from deareis import mpl
project = Project.from_file("../../tests/example-project-v6.json")
for plot in project.get_plots():
  if "DRT" not in plot.get_label():
    continue
  figure, axes = mpl.plot(plot, project)
  break