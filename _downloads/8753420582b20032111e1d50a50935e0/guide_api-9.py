from deareis import Project
project = Project.from_file("../../tests/example-project-v6.json")
data = project.get_data_sets()[0]
fit = project.get_fits(data)[0]
fit.circuit.to_drawing().draw()
fit.circuit.to_drawing(running=True).draw()