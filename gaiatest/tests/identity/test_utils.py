from gaiatest import GaiaTestCase
import gaiatest.tests.identity.utils as utils

class TestUtils(GaiaTestCase):
    """
    This module's utility functions work correctly
    """

    test_assertion = "eyJhbGciOiJSUzI1NiJ9.eyJwdWJsaWMta2V5Ijp7ImFsZ29yaXRobSI6IkRTIiwieSI6IjUxZWMzOTZkMTIxZjU4MmQ4MDlkMDRjYzdmY2M4ODg2OTA4YzQ0ZGM5MDZmZDhlOGE2NTg4NzZkMzcwZjIwOWVhZmY4YTVlNTQzYzZkNTRlN2Y0MDNhMWFiYjllYjNmYWM0MTZkNjliNjZlNmNhMzljMTcwNGM5NTBhMjlmNmU2ZTA5YzIzOGFlNDE2MjMxM2JmMzNjZTRhODQ0ZTRhOGY3YjZlZWE2NTEwNDRiMTExN2FkY2RmN2NkNDcxMGE0NmQ3NDcxYzQ3NzlkNzdhODA2MWZkNTdhMjFmZTM1MDcxMmEzYzllYjFiMGJlMTdkOWU5MDhmOWZmYzMyYTg3M2UiLCJwIjoiZmY2MDA0ODNkYjZhYmZjNWI0NWVhYjc4NTk0YjM1MzNkNTUwZDlmMWJmMmE5OTJhN2E4ZGFhNmRjMzRmODA0NWFkNGU2ZTBjNDI5ZDMzNGVlZWFhZWZkN2UyM2Q0ODEwYmUwMGU0Y2MxNDkyY2JhMzI1YmE4MWZmMmQ1YTViMzA1YThkMTdlYjNiZjRhMDZhMzQ5ZDM5MmUwMGQzMjk3NDRhNTE3OTM4MDM0NGU4MmExOGM0NzkzMzQzOGY4OTFlMjJhZWVmODEyZDY5YzhmNzVlMzI2Y2I3MGVhMDAwYzNmNzc2ZGZkYmQ2MDQ2MzhjMmVmNzE3ZmMyNmQwMmUxNyIsInEiOiJlMjFlMDRmOTExZDFlZDc5OTEwMDhlY2FhYjNiZjc3NTk4NDMwOWMzIiwiZyI6ImM1MmE0YTBmZjNiN2U2MWZkZjE4NjdjZTg0MTM4MzY5YTYxNTRmNGFmYTkyOTY2ZTNjODI3ZTI1Y2ZhNmNmNTA4YjkwZTVkZTQxOWUxMzM3ZTA3YTJlOWUyYTNjZDVkZWE3MDRkMTc1ZjhlYmY2YWYzOTdkNjllMTEwYjk2YWZiMTdjN2EwMzI1OTMyOWU0ODI5YjBkMDNiYmM3ODk2YjE1YjRhZGU1M2UxMzA4NThjYzM0ZDk2MjY5YWE4OTA0MWY0MDkxMzZjNzI0MmEzODg5NWM5ZDViY2NhZDRmMzg5YWYxZDdhNGJkMTM5OGJkMDcyZGZmYTg5NjIzMzM5N2EifSwicHJpbmNpcGFsIjp7ImVtYWlsIjoib3NjYXIxNTYzMEBwZXJzb25hdGVzdHVzZXIub3JnIn0sImlhdCI6MTM1NTc3MTczMzM1MCwiZXhwIjoxMzU1Nzc1MzMzMzUwLCJpc3MiOiJsb2dpbi5wZXJzb25hLm9yZyJ9.S6X00SuSeUhbQ3QIsx1Z8xcwJdbiHtP7pEGNaBxvaDWfdQwP0scQEJe2_jhHtC-ZfPfi1PbMMpSPFdieaYP4JeDOC_f2h4ojDJX-yNPYPA7DUcSS0Zv7eGNSqL0hLOB5iRTWGTLyrnX_kgiXw6wVhoO8evfE_fb5ckDW3mG5BA-O3eKEjIVI-L-9ZZmab-11IRrUG2GQwI0Hq38dSKEULblqWuB92AIWWIsSd-TiyUKLzTuINzqFZ8ZiK02ePZHcA4rIYTMCEuTGq6wZgxdgD-t05c3bdEbag8ghACJINnS5CEmBT6hDUSXADYUyIJogPeq1LZDpAA8HpSLx8avzMw~eyJhbGciOiJEUzEyOCJ9.eyJleHAiOjEzNTU3NzE4NTMzNzcsImF1ZCI6Imh0dHA6Ly9wZW9wbGUubW96aWxsYS5vcmcifQ.xz64hSz0TWPW9y92J_-U0oHvPCdSULN2TXuk9RywQyepPe6cnXrSJg"

    def testAssertionUtils(self):
        """
        Our utility functions can correctly unpack an assertion
        """
        assertion = utils.unpackAssertion(self.test_assertion)

        # nb, the timestamps are milliseconds since the unix epoch
        self.assertEqual(assertion['claim']['exp'], 1355775333350)
        self.assertEqual(assertion['claim']['principal']['email'], 'oscar15630@personatestuser.org')
        self.assertEqual(assertion['payload']['aud'], "http://people.mozilla.org");
        self.assertEqual(assertion['payload']['exp'], 1355771853377)


