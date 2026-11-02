from deareis import Project, mpl
project = Project.from_file("../../tests/example-project-v6.json")
for data in project.get_data_sets():
  figure, axes = mpl.plot_data(
    data,
    colored_axes=True,
    legend=False,
  )
  figure.tight_layout()
  break