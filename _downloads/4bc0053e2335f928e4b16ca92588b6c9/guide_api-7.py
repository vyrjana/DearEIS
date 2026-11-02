from deareis import Project, mpl
project = Project.from_file("../../tests/example-project-v6.json")
for plot in project.get_plots():
  figure, axes = mpl.plot(plot, project)
  figure.tight_layout()
  break