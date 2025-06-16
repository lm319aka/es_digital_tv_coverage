import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self):
        import tdtc
        self.tdtc = tdtc

    def test_get_individual_coverage_data(self):
        data, driver, wait = self.tdtc.coverage_tdt("01000")
        self.assertEqual(
            data,
            {'Postal code': '01000', 'Populations': [{'Population': 'CACERES', 'Data': []}]}
        )  # add assertion here

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
