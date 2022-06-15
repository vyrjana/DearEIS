# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from unittest import TestCase
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    format_number,
    format_timestamp,
)
from numpy import array, nan, inf
from datetime import datetime


class TestUtility(TestCase):
    def test_01_format_timestamp(self):
        self.assertEqual(
            format_timestamp(datetime(2015, 4, 28, 0, 0, 0).timestamp()),
            "2015-04-28 00:00:00",
        )
        with self.assertRaises(AssertionError):
            format_timestamp("test")
            format_timestamp([])
            format_timestamp(5)
            format_timestamp(None)

    def test_02_window_pos_dims(self):
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

    def test_03_align_numbers(self):
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

    def test_04_format_number(self):
        self.assertEqual(format_number(nan), "-")
        self.assertEqual(format_number(inf), "INF")
        self.assertEqual(format_number(-inf), "-INF")
        self.assertEqual(format_number(5.6230364), "5.6    ")
        self.assertEqual(format_number(5.6230364, decimals=4), "5.6230    ")
        self.assertEqual(format_number(5.6230364, width=10), "   5.6    ")
        self.assertEqual(format_number(5.6230364, exponent=False), "5.6")
        self.assertEqual(format_number(5.6230364e-5, exponent=False), "0.0")
        self.assertEqual(format_number(5.6230364e-5, exponent=True), "56.2E-06")
        self.assertEqual(
            format_number(5.6230364e-5, decimals=0, exponent=True), "56E-06"
        )
        self.assertEqual(
            format_number(5.6230364e-5, significants=4, exponent=True), "56.23E-06"
        )
        self.assertEqual(
            format_number(5.6230364e4, significants=4, exponent=True), "56.23E+03"
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
