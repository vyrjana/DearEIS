# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from unittest import TestCase
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    format_latex_element,
    format_latex_unit,
    format_latex_value,
    format_number,
    format_timestamp,
    process_cdc,
)
from pyimpspec import Circuit
from numpy import (
    array,
    nan,
    inf,
)
from datetime import datetime
from typing import Optional


class TestUtility(TestCase):
    def test_format_timestamp(self):
        self.assertEqual(
            format_timestamp(datetime(2015, 4, 28, 0, 0, 0).timestamp()),
            "2015-04-28 00:00:00",
        )
        with self.assertRaises(AssertionError):
            format_timestamp("test")
            format_timestamp([])
            format_timestamp(5)
            format_timestamp(None)

    def test_window_pos_dims(self):
        with self.assertRaises(AssertionError):
            calculate_window_position_dimensions(0, 0)
            calculate_window_position_dimensions(0.0, 0.0)
            calculate_window_position_dimensions(-126, 562)
            calculate_window_position_dimensions(9, 4)
            calculate_window_position_dimensions(-5.0, 8.0)
            calculate_window_position_dimensions(2.0, -5.0)
            calculate_window_position_dimensions(True, 2)
            calculate_window_position_dimensions(2, True)
            calculate_window_position_dimensions(None, 2)
            calculate_window_position_dimensions(2, None)
            calculate_window_position_dimensions("test", 6.1)
            calculate_window_position_dimensions(636.2, "test")

    def test_align_numbers(self):
        self.assertEqual(
            align_numbers(
                [
                    "-62.9",
                    "5.03",
                    "3.8",
                    "4",
                ]
            ),
            [
                "-62.9",
                "  5.03",
                "  3.8",
                "  4",
            ],
        )
        with self.assertRaises(AssertionError):
            align_numbers(set(["a", "0"]))
            align_numbers(array([1, 5, 23]))
            align_numbers(["6", "as", 1, True])

    def test_format_number(self):
        self.assertEqual(format_number(nan), "NaN")
        self.assertEqual(format_number(inf), "INF")
        self.assertEqual(format_number(-inf), "-INF")
        self.assertEqual(format_number(5.6230364), "5.6")
        self.assertEqual(format_number(5.6230364, decimals=4), "5.6230")
        self.assertEqual(format_number(5.6230364, width=10), "       5.6")
        self.assertEqual(format_number(5.6230364, exponent=False), "5.6")
        self.assertEqual(format_number(5.6230364e-5, exponent=False), "0.0")
        self.assertEqual(format_number(5.6230364e-5, exponent=True), "56.2e-06")
        self.assertEqual(
            format_number(5.6230364e-5, decimals=0, exponent=True), "56e-06"
        )
        self.assertEqual(
            format_number(5.6230364e-5, significants=4, exponent=True), "56.23e-06"
        )
        self.assertEqual(
            format_number(5.6230364e4, significants=4, exponent=True), "56.23e+03"
        )
        with self.assertRaises(ValueError):
            format_number("test")
            format_number([])
            format_number(True)
        with self.assertRaises(AssertionError):
            format_number(2.0, decimals=2.5)
            format_number(2.0, width=2.0)
            format_number(2.0, exponent=1)
            format_number(2.0, significants=2.5)
            format_number(2.0, significants=-1)

    def test_process_cdc(self):
        circuit: Optional[Circuit]
        msg: str
        circuit, msg = process_cdc("(RC)")
        self.assertIsInstance(circuit, Circuit)
        self.assertEqual(msg, "")
        circuit, msg = process_cdc("(RC")
        self.assertEqual(circuit, None)
        self.assertNotEqual(msg, "")
        circuit, msg = process_cdc("Tlm{Zeta=inf}")
        self.assertEqual(circuit, None)
        self.assertNotEqual(msg, "")

    def test_format_latex_value(self):
        self.assertEqual(format_latex_value(5321), "5.32e+03")
        self.assertEqual(format_latex_value(5321, fmt="{:.6e}"), "5.321000e+03")
        self.assertEqual(format_latex_value(5321, fmt="{:.6g}"), "5321")
        self.assertEqual(format_latex_value(1.3562e2), "136")
        self.assertEqual(format_latex_value(1.3562e7), "1.36e+07")
        self.assertEqual(format_latex_value(1.3562e2, fmt="{:.5e}"), "1.35620e+02")
        self.assertEqual(format_latex_value(1.3562e2, fmt="{:.5g}"), "135.62")
        self.assertEqual(format_latex_value("test"), "test")
        self.assertEqual(format_latex_value(True), "True")

    def test_format_latex_unit(self):
        self.assertEqual(format_latex_unit(""), r"")
        self.assertEqual(format_latex_unit("F"), r"$\rm F$")
        self.assertEqual(format_latex_unit("S/s"), r"$\rm S / s$")
        self.assertEqual(format_latex_unit("ohm*s"), r"$\rm ohm \times s$")
        self.assertEqual(format_latex_unit("ohm/s^(1/2)"), r"$\rm ohm / s^{1 / 2}$")
        self.assertEqual(format_latex_unit("S*s^(1/2)"), r"$\rm S \times s^{1 / 2}$")

    def test_format_latex_element(self):
        self.assertEqual(format_latex_element("Q"), r"$\rm Q$")
        self.assertEqual(format_latex_element("R_62"), r"$\rm R_{62}$")
        self.assertEqual(format_latex_element("C_dl"), r"$\rm C_{dl}$")
        with self.assertRaises(AssertionError):
            format_latex_element("C_dl_2")
