from deareis import Project, mpl
project = Project.from_file("../../tests/example-project-v6.json")
for data in project.get_data_sets():
  for zhit in project.get_zhits(data):
    figure, axes = mpl.plot_fit(
      zhit,
      data=data,
      colored_axes=True,
      legend=False,
    )
    figure.tight_layout()
    break
  break