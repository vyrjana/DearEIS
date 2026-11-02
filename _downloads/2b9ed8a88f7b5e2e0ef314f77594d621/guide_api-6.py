from deareis import Project, mpl
project = Project.from_file("../../tests/example-project-v6.json")
for sim in project.get_simulations():
  figure, axes = mpl.plot_nyquist(
    sim,
    line=True,
    colored_axes=True,
    legend=False,
  )
  figure.tight_layout()
  break