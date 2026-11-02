from deareis import mpl
import pyimpspec
from numpy import logspace, log10 as log

data = pyimpspec.generate_mock_data("CIRCUIT_1", noise=5e-2, seed=42)[0]
circuit = pyimpspec.generate_mock_circuits("CIRCUIT_1")[0]
f = data.get_frequencies()
figure, axes = mpl.plot_circuit(circuit, frequencies=f, label="TC-1", title="", legend=False, colored_axes=True)
figure.tight_layout()
mpl.show()

data = pyimpspec.simulate_spectrum(
  circuit,
  logspace(
    log(max(f)),
    log(min(f)),
    num=int(log(max(f)) - log(min(f))) * 100 + 1,
  ),
  label="TC-1",
)
figure, axes = mpl.plot_nyquist(data, line=True)
figure.tight_layout()
mpl.show()

figure, axes = mpl.plot_bode(data, line=True)
figure.tight_layout()
mpl.show()