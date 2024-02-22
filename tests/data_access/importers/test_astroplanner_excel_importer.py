import unittest

from assertpy import assert_that

from app.utils.astroplanner_excel_importer import AstroPlannerExcelImporter


class TestAstroPlannerExcelImporter(unittest.TestCase):

    def test_normalize_size_arcminutes(self):
        assert_that(AstroPlannerExcelImporter.normalize_size("30'")).is_equal_to(30.0)

    def test_normalize_size_arcseconds(self):
        assert_that(AstroPlannerExcelImporter.normalize_size('30"')).is_equal_to(0.5)

    def test_normalize_size_numeric(self):
        assert_that(AstroPlannerExcelImporter.normalize_size(0.5)).is_equal_to(0.5)

    def test_normalize_size_invalid_input(self):
        with self.assertRaises(ValueError):
            AstroPlannerExcelImporter.normalize_size('invalid')
