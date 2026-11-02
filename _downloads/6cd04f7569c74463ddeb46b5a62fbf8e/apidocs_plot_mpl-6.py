from deareis import mpl
import pyimpspec
import pyimpspec.plot.colors as colors

data = pyimpspec.generate_mock_data("CIRCUIT_1", noise=5e-2, seed=42)[0]
mu_criterion = 0.85
tests, suggestion = pyimpspec.perform_exploratory_kramers_kronig_tests(
  data,
  mu_criterion=mu_criterion,
  add_capacitance=True,
)
test, scores, lower_limit, upper_limit = suggestion


figure, axes = mpl.plot_kramers_kronig_tests(
  tests,
  suggestion,
  data,
  legend=False,
  colored_axes=True,
)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_pseudo_chisqr(
  tests,
  lower_limit=lower_limit,
  upper_limit=upper_limit,
)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_num_RC_suggestion(suggestion)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_residuals(test)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_nyquist(
  data,
  colors={"impedance": colors.COLOR_BLACK},
  legend=False,
)
_ = mpl.plot_nyquist(
  test,
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
  test,
  line=True,
  figure=figure,
  axes=axes,
)
figure.tight_layout()
mpl.show()