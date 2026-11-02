from deareis import mpl
import pyimpspec
import pyimpspec.plot.colors as colors

data = pyimpspec.generate_mock_data("CIRCUIT_1", noise=5e-2, seed=42)[0]
circuit = pyimpspec.parse_cdc("R(RC)(RW)")
fit = pyimpspec.fit_circuit(circuit, data=data)

figure, axes = mpl.plot_fit(
  fit,
  data,
  legend=False,
  colored_axes=True,
)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_nyquist(
  data,
  colors={"impedance": colors.COLOR_BLACK},
  legend=False,
)
_ = mpl.plot_nyquist(
  fit,
  line=True,
  figure=figure,
  axes=axes,
)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_bode(
  data,
  colors={
    "magnitude": colors.COLOR_BLACK,
    "phase": colors.COLOR_BLACK,
  },
  legend=False,
)
_ = mpl.plot_bode(
  fit,
  line=True,
  figure=figure,
  axes=axes,
)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_residuals(fit)
figure.tight_layout()
mpl.show()