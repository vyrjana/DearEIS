from deareis import mpl
import pyimpspec
import pyimpspec.plot.colors as colors

data = pyimpspec.generate_mock_data("CIRCUIT_1", noise=5e-2, seed=42)[0]
figure, axes = mpl.plot_data(data, legend=False, colored_axes=True)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_nyquist(data)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_bode(data)
figure.tight_layout()
mpl.show()