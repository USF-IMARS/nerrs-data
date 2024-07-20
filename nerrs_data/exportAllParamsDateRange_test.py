
from unittest import TestCase

import nerrs_data

class Test_exportAllParamsDateRange_main(TestCase):

    def test_calls_my_method(self):
        nerrs_data.exportAllParamsDateRange(
            stationCode='acespwq',
            minDate='2023-01-01',
            maxDate='2023-01-02',
            paramTested=None
        )
