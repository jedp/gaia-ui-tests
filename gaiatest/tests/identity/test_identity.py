import gaiatest.tests.identity.utils as utils
from gaiatest.tests.identity.utils import IdentityTestCase
import time

# When gaia is built with DEBUG=1, the origin will be http://, 
# otherwise it will be app://.  So you may have to change this
# accordingly
AUDIENCE = "app://uitest.gaiamobile.org"
#AUDIENCE = "http://uitest.gaiamobile.org:8080"

class TestIdentity(IdentityTestCase):

    # Test app selectors
    _app_issuer_name = ('id', 'issuer-name')
    _app_unverified_ok = ('id', 'unverified-ok')
    _app_request = ('id', 't-request')
    _app_request_with_oncancel = ('id', 't-request-withOnCancel')
    _app_request_allow_unverified = ('id', 't-request-allowUnverified')
    _app_request_force_issuer = ('id', 't-request-forceIssuer')
    _app_request_force_issuer_allow_unverified = ('id', 't-request-forceIssuer-allowUnverified')
    _app_logout = ('id', 't-logout')
    _app_events = ('id', 'event-stream')
    _app_ready_event = ('css selector', 'li.ready')
    _app_logout_event = ('css selector', 'li.logout')
    _app_login_event = ('css selector', 'li.login')
    _app_cancel_event = ('css selector', 'li.cancel')
    _app_login_assertion_text = ('css selector', 'li.login div.assertion')

    # Trusty UI on home screen
    _tui_container = ('id', 'trustedui-frame-container')
    _tui_close = ('id', 'trustedui-close')

    # Persona dialog selectors
    _bid_content = ('css selector', 'div.table')
    _bid_username = ('id', 'authentication_email')
    _bid_password = ('id', 'authentication_password')
    _bid_new_password = ('id', 'password')
    _bid_verify_new_password = ('id', 'vpassword')
    _bid_verify_button = ('id', 'verify_user')
    _bid_start_button = ('css selector', 'button.start')
    _bid_return_button = ('css selector', 'button.returning')
    _bid_sign_in = ('id', 'signInButton')
    _bid_use_new_email = ('id', 'useNewEmail')
    _bid_not_me = ('id', 'thisIsNotMe')

    def testIdentityEnabled(self):
        "Native identity is enabled"
        self.assertEqual(True, self.marionette.execute_script(
            """return SpecialPowers.getBoolPref("dom.identity.enabled");""", 
            special_powers=True))

    def testRequest(self):
        "We can request an identity"
        test_email, test_pass = utils.getTestUser()

        self.wait_for_element_present(*self._app_ready_event)
        self.clearEventList()
        self.hit(self.marionette.find_element(*self._app_request))

        # switch over to the main system app frame and get the person dialog
        self.marionette.switch_to_frame()
        self.wait_for_element_present(*self._tui_container)
        trustyUI = self.marionette.find_element(*self._tui_container)
        personaDialog = trustyUI.find_element('tag name', 'iframe')
        self.marionette.switch_to_frame(personaDialog)

        self.wait_for_element_displayed(*self._bid_content)
        notMe = self.marionette.find_elements(*self._bid_not_me)
        if notMe:
            self.hit(notMe[0])

        # sign in with persona
        self.wait_for_element_displayed(*self._bid_username)
        self.marionette.find_element(*self._bid_username).send_keys(test_email)
        self.hit(self.marionette.find_element(*self._bid_start_button))
        self.wait_for_element_displayed(*self._bid_password)
        self.marionette.find_element(*self._bid_password).send_keys(test_pass)
        self.hit(self.marionette.find_element(*self._bid_return_button))

        # switch back to the test app
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame_id)
        self.marionette.switch_to_frame(0)

        # get the assertion
        self.wait_for_element_displayed(*self._app_login_event)
        assertion = self.marionette.find_element(*self._app_login_assertion_text).text
        unpacked = utils.unpackAssertion(assertion)
        utils.printAssertionSummary(unpacked)

        # sanity-check the assertion
        self.assertEqual(AUDIENCE, unpacked['payload']['aud'])
        self.assertEqual(test_email, unpacked['claim']['principal']['email'])

        # check with the verifier
        verified = utils.verifyAssertion(assertion, AUDIENCE)
        self.assertEqual(verified['status'], 'okay')
        self.assertEqual(verified['email'], test_email)
        self.assertEqual(verified['audience'], AUDIENCE)

        time.sleep(1) 

    def testRequestCancel(self):
        "Canceled requests can callback to an oncancel handler"
        self.wait_for_element_present(*self._app_ready_event)
        self.clearEventList()
        self.hit(self.marionette.find_element(*self._app_request_with_oncancel))

        # switch over to the main system app frame, get the trusted ui
        # and close it
        self.marionette.switch_to_frame()
        self.wait_for_element_present(*self._tui_close)
        self.hit(self.marionette.find_element(*self._tui_close))

        # switch back to the test app
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame_id)
        self.marionette.switch_to_frame(0)
    
        # check that oncancel left its mark
        self.wait_for_element_displayed(*self._app_cancel_event)
        time.sleep(1)

    def testAllowUnverified(self):
        "We can get an unverified email"
        randomName = utils.randomName()
        test_unverified_email, test_pass = "%s@everypony.com" % (randomName), "purple ponycorn"

        self.wait_for_element_present(*self._app_ready_event)
        self.clearEventList()
        self.hit(self.marionette.find_element(*self._app_unverified_ok))

        self.hit(self.marionette.find_element(*self._app_request_allow_unverified))

        # switch over to the main system app frame and get the person dialog
        self.marionette.switch_to_frame()
        self.wait_for_element_present(*self._tui_container)
        trustyUI = self.marionette.find_element(*self._tui_container)
        personaDialog = trustyUI.find_element('tag name', 'iframe')
        self.marionette.switch_to_frame(personaDialog)

        self.wait_for_element_displayed(*self._bid_content)
        notMe = self.marionette.find_elements(*self._bid_not_me)
        if notMe:
            self.hit(notMe[0])

        # sign in with persona
        self.wait_for_element_displayed(*self._bid_username)
        self.marionette.find_element(*self._bid_username).send_keys(test_unverified_email)
        self.hit(self.marionette.find_element(*self._bid_start_button))
        self.wait_for_element_displayed(*self._bid_new_password)
        self.marionette.find_element(*self._bid_new_password).send_keys(test_pass)
        self.wait_for_element_displayed(*self._bid_verify_new_password)
        self.marionette.find_element(*self._bid_verify_new_password).send_keys(test_pass)
        self.hit(self.marionette.find_element(*self._bid_verify_button))

        # switch back to the test app
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame_id)
        self.marionette.switch_to_frame(0)

        # see the unverified-email assertion!
        self.wait_for_element_displayed(*self._app_login_event)
        loginEvent = self.marionette.find_element(*self._app_login_event)
        assertion = self.marionette.find_element(*self._app_login_assertion_text).text
        unpacked = utils.unpackAssertion(assertion)
        utils.printAssertionSummary(unpacked)
        self.assertEqual(test_unverified_email, unpacked['claim']['principal']['unverified-email'])

        # check with the verifier
        verified = utils.verifyAssertion(assertion, AUDIENCE, allowUnverified='true')
        self.assertEqual(verified['status'], 'okay')
        self.assertEqual(verified['unverified-email'], test_unverified_email)
        self.assertEqual(verified['audience'], AUDIENCE)

        time.sleep(1) 

    def testForceIssuer(self):
        "We can force the issuer"
        test_email, test_pass = utils.getTestUser()
        test_iss = "b2g2pac.personatest.org"

        self.wait_for_element_present(*self._app_ready_event)
        self.clearEventList()
        self.marionette.find_element(*self._app_issuer_name).send_keys(test_iss)

        self.hit(self.marionette.find_element(*self._app_request_force_issuer))

        # switch over to the main system app frame and get the person dialog
        self.marionette.switch_to_frame()
        self.wait_for_element_present(*self._tui_container)
        trustyUI = self.marionette.find_element(*self._tui_container)
        personaDialog = trustyUI.find_element('tag name', 'iframe')
        self.marionette.switch_to_frame(personaDialog)

        self.wait_for_element_displayed(*self._bid_content)
        notMe = self.marionette.find_elements(*self._bid_not_me)
        if notMe:
            self.hit(notMe[0])

        # sign in with persona
        self.wait_for_element_displayed(*self._bid_username)
        self.marionette.find_element(*self._bid_username).send_keys(test_email)
        self.hit(self.marionette.find_element(*self._bid_start_button))
        self.wait_for_element_displayed(*self._bid_password)
        self.marionette.find_element(*self._bid_password).send_keys(test_pass)
        self.hit(self.marionette.find_element(*self._bid_return_button))

        # switch back to the test app
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame_id)
        self.marionette.switch_to_frame(0)

        # see the assertion
        self.wait_for_element_displayed(*self._app_login_event)
        loginEvent = self.marionette.find_element(*self._app_login_event)
        assertion = self.marionette.find_element(*self._app_login_assertion_text).text
        unpacked = utils.unpackAssertion(assertion)
        utils.printAssertionSummary(unpacked)
        self.assertEqual(test_email, unpacked['claim']['principal']['email'])
        self.assertEqual(test_iss, unpacked['claim']['iss'])

        # check with the verifier
        verified = utils.verifyAssertion(assertion, AUDIENCE, forceIssuer=test_iss)
        self.assertEqual(verified['status'], 'okay')
        self.assertEqual(verified['email'], test_email)
        self.assertEqual(verified['audience'], AUDIENCE)
        self.assertEqual(verified['issuer'], test_iss)

    def testForceIssuerAllowUnverified(self):
        "We can force the issuer with an unverified email"
        randomName = utils.randomName()
        test_unverified_email = "%s@everypony.com" % (randomName)
        test_pass = "purple ponycorn"
        test_iss = "b2g2pac.personatest.org"

        self.wait_for_element_present(*self._app_ready_event)
        self.clearEventList()
        self.hit(self.marionette.find_element(*self._app_unverified_ok))
        self.marionette.find_element(*self._app_issuer_name).send_keys(test_iss)

        self.hit(self.marionette.find_element(*self._app_request_force_issuer_allow_unverified))

        # switch over to the main system app frame and get the person dialog
        self.marionette.switch_to_frame()
        self.wait_for_element_present(*self._tui_container)
        trustyUI = self.marionette.find_element(*self._tui_container)
        personaDialog = trustyUI.find_element('tag name', 'iframe')
        self.marionette.switch_to_frame(personaDialog)

        self.wait_for_element_displayed(*self._bid_content)
        notMe = self.marionette.find_elements(*self._bid_not_me)
        if notMe:
            self.hit(notMe[0])

        # sign in with persona
        self.wait_for_element_displayed(*self._bid_username)
        self.marionette.find_element(*self._bid_username).send_keys(test_unverified_email)
        self.hit(self.marionette.find_element(*self._bid_start_button))
        self.wait_for_element_displayed(*self._bid_new_password)
        self.marionette.find_element(*self._bid_new_password).send_keys(test_pass)
        self.wait_for_element_displayed(*self._bid_verify_new_password)
        self.marionette.find_element(*self._bid_verify_new_password).send_keys(test_pass)
        self.hit(self.marionette.find_element(*self._bid_verify_button))

        # switch back to the test app
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame_id)
        self.marionette.switch_to_frame(0)

        # see the unverified-email assertion!
        self.wait_for_element_displayed(*self._app_login_event)
        loginEvent = self.marionette.find_element(*self._app_login_event)
        assertion = self.marionette.find_element(*self._app_login_assertion_text).text
        unpacked = utils.unpackAssertion(assertion)
        utils.printAssertionSummary(unpacked)
        self.assertEqual(test_unverified_email, unpacked['claim']['principal']['unverified-email'])
        self.assertEqual(test_iss, unpacked['claim']['iss'])

        # check with the verifier
        verified = utils.verifyAssertion(assertion, AUDIENCE, allowUnverified='true', forceIssuer=test_iss)
        self.assertEqual(verified['status'], 'okay')
        self.assertEqual(verified['unverified-email'], test_unverified_email)
        self.assertEqual(verified['audience'], AUDIENCE)
        self.assertEqual(verified['issuer'], test_iss)

        time.sleep(1) 


    def testLogout(self):
        "We can logout"
        self.wait_for_element_displayed(*self._app_logout)
        self.hit(self.marionette.find_element(*self._app_logout))
        # hard - this can be 'ready' or 'logout' - how to check for either?
        #self.wait_for_element_displayed(*self._app_logout_event)





