# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from unittest import TestCase
from deareis.utility import (
    format_timestamp,
    dict_to_csv,
    window_pos_dims,
    align_numbers,
    number_formatter,
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

    def test_02_dict_to_csv(self):
        self.assertEqual(
            dict_to_csv(
                {
                    "a": [1, 4, 7],
                    "b": array([5, 2, 8]),
                    "c": ["No", "Yes", "Huh?"],
                },
            ),
            "a,b,c\n1,5,No\n4,2,Yes\n7,8,Huh?\n",
        )
        with self.assertRaises(AssertionError):
            dict_to_csv(True)
            dict_to_csv(1)
            dict_to_csv(2.5)
            dict_to_csv("Test")
            dict_to_csv([])
            dict_to_csv(set())

    def test_03_window_pos_dims(self):
        with self.assertRaises(AssertionError):
            window_pos_dims(0, 0)
            window_pos_dims(0.0, 0.0)
            window_pos_dims(-126, 562)
            window_pos_dims(9, 4)
            window_pos_dims(-5.0, 8.0)
            window_pos_dims(2.0, -5.0)
            window_pos_dims(True, 2)
            window_pos_dims(2, True)
            window_pos_dims(None, 2)
            window_pos_dims(2, None)
            window_pos_dims("test", 6.1)
            window_pos_dims(636.2, "test")

    def test_04_align_numbers(self):
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

    def test_05_number_formatter(self):
        self.assertEqual(number_formatter(nan), "-")
        self.assertEqual(number_formatter(inf), "INF")
        self.assertEqual(number_formatter(-inf), "-INF")
        self.assertEqual(number_formatter(5.6230364), "5.6    ")
        self.assertEqual(number_formatter(5.6230364, decimals=4), "5.6230    ")
        self.assertEqual(number_formatter(5.6230364, width=10), "   5.6    ")
        self.assertEqual(number_formatter(5.6230364, exponent=False), "5.6")
        self.assertEqual(number_formatter(5.6230364e-5, exponent=False), "0.0")
        self.assertEqual(number_formatter(5.6230364e-5, exponent=True), "56.2E-06")
        self.assertEqual(
            number_formatter(5.6230364e-5, decimals=0, exponent=True), "56E-06"
        )
        self.assertEqual(
            number_formatter(5.6230364e-5, significants=4, exponent=True), "56.23E-06"
        )
        self.assertEqual(
            number_formatter(5.6230364e4, significants=4, exponent=True), "56.23E+03"
        )
        with self.assertRaises(ValueError):
            number_formatter("test")
            number_formatter([])
            number_formatter(True)
        with self.assertRaises(AssertionError):
            number_formatter(2.0, decimals=2.5)
            number_formatter(2.0, width=2.0)
            number_formatter(2.0, exponent=1)
            number_formatter(2.0, significants=2.5)
            number_formatter(2.0, significants=-1)
