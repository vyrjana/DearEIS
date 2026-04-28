from pyimpspec import parse_cdc
# A Warburg impedance is used here just to have two different symbols
circuit = parse_cdc("(WR)")
elements = circuit.get_elements()
custom_labels = {
    elements[0]: r"$Z_{\rm data}$",
    elements[1]: r"$R_{\rm par}$",
}
circuit.to_drawing(custom_labels=custom_labels).draw()