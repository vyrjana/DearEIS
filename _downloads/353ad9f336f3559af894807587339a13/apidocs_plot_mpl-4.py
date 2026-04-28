from deareis import mpl
import pyimpspec
import pyimpspec.plot.colors as colors

data = pyimpspec.generate_mock_data("CIRCUIT_1", noise=5e-2, seed=42)[0]
drt = pyimpspec.analysis.drt.calculate_drt_tr_rbf(data)
figure, axes = mpl.plot_drt(
  drt,
  data,
  legend=False,
  colored_axes=True,
)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_real_imaginary(
  data,
  colors={
    "real": colors.COLOR_BLACK,
    "imaginary": colors.COLOR_BLACK,
  },
  legend=False,
)
_ = mpl.plot_real_imaginary(
  drt,
  line=True,
  figure=figure,
  axes=axes,
)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_gamma(drt)
figure.tight_layout()
mpl.show()


figure, axes = mpl.plot_residuals(drt)
figure.tight_layout()
mpl.show()