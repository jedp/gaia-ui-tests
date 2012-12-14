from gaiatest import GaiaTestCase
import urllib
import requests
import base64
import json
from datetime import datetime
import time

PREF_SYNTHETIC_EVENTS_OK = "dom.identity.syntheticEventsOk"
VERIFIER_URL = "https://login.native-persona.org/verify"

def decodeB64(b64input):
    """
    Add padding to b64input if necessary.  I think python's base64
    implementation is broken and this should not be necessary.
    """
    out = b64input.strip()
    lastBytesLen = len(out) % 4
    if lastBytesLen == 0:
        pass
    elif lastBytesLen == 3:
        out += '='
    elif lastBytesLen == 2:
        out += '=='
    else:
        print out, lastBytesLen
        raise Exception("Bad base64 input; last group contained weird number of bytes.")

    return base64.b64decode(out)

def decode(encoded):
    return json.loads(decodeB64(encoded))

def unpackAssertion(assertion):
    # ignore signatures; we're not a verifier
    header, claim, _, payload, _ = assertion.split('.');
    return {"header": decode(header),
            "claim": decode(claim),
            "payload": decode(payload)}

def randomName():
    return "ponycorn%d" % (int(time.time()))

def printAssertionSummary(data):
    email = data['claim']['principal'].get('email', '')
    unverified_email = data['claim']['principal'].get('unverified-email', '')
    exp = datetime.fromtimestamp(int(data['payload']['exp']) / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    iss = data['claim']['iss']
    aud = data['payload']['aud']

    print """\
 Issuer:           %(iss)s
 Audience:         %(aud)s
 Email:            %(email)s
 Unverified Email: %(unverified_email)s
 Expires:          %(exp)s
""" % (vars())

def verifyAssertion(assertion, audience, **params):
    data = {'assertion': assertion, 'audience': audience}
    data.update(params)

    return requests.post(VERIFIER_URL, data=data).json()

def getTestUser():
    print "\nNOTICE: Getting a new username and email from personatestuser.org ..."
    params = urllib.urlencode({
        "browserid": "native-persona.org",
        "verifier": "native-persona.org/verify"
    })

    f = urllib.urlopen("http://personatestuser.org/email/custom?%s" % (params,))
    data = json.loads(f.read())

    if not data['email']:
        raise Exception("personatestuser did not return an email: " + str(data))

    print "\nGot new test user:", data['email'], "password:", data['pass']

    return (data['email'], data['pass'])

class IdentityTestCase(GaiaTestCase):
    __is_desktop = None

    def clearEventList(self):
        script = """
            var eventStream = document.getElementById('event-stream');
            if (eventStream.hasChildNodes()) {
              while(eventStream.childNodes.length > 0) {
                eventStream.removeChild(eventStream.firstChild);
              }
            }
        """
        self.marionette.execute_script(script)

    def isDesktopBuild(self):
        if self.__is_desktop is None:
            self.__is_desktop = self.marionette.session_capabilities['platform'] in ['Linux', 'Darwin']
            print "NOTICE: tests/identity thinks this", (self.__is_desktop and "is" or "is not"), "a desktop build."
        return self.__is_desktop 

    def hit(self, element):
        """
        A wrapper that calls tap() on device builds, and click() on desktop
        builds.  Since tap() does not work on desktop, and click() does not
        work on device, we must do something.
        """
        if self.isDesktopBuild():
            element.click()
        else:
            self.marionette.tap(element)

    def setUp(self):
        GaiaTestCase.setUp(self)

        if self.wifi:
            self.data_layer.enable_wifi()
            self.data_layer.connect_to_wifi(self.testvars['wifi'])

        # Bug 822450 - Signal to nsDOMIdentity that it's ok to accept synthetic
        # clicks, until marionette can produce native events.
        setPref = """SpecialPowers.setBoolPref("%s", true);""" % PREF_SYNTHETIC_EVENTS_OK
        getPref = """return SpecialPowers.getBoolPref("%s");""" % PREF_SYNTHETIC_EVENTS_OK
        self.marionette.execute_script(setPref, special_powers=True);
        self.assertEqual(True, self.marionette.execute_script(getPref, special_powers=True))

        # Send a message to the b2g identity component to clear state
        self.marionette.set_context("chrome")
        self.marionette.execute_script("""
            Components.classes["@mozilla.org/observer-service;1"]
                .getService(Components.interfaces.nsIObserverService)
                .notifyObservers(null, "identity-controller-reset", {});
            """)
        self.marionette.set_context("content")

        # launch the ui tests app, which contains the navigator.id tests
        self.app = self.apps.launch('UI tests')

        # launch the nav.id tests
        self.wait_for_element_displayed('link text', 'navigator.mozId tests')
        self.hit(self.marionette.find_element('link text', 'navigator.mozId tests'))
        self.marionette.switch_to_frame(0)


    def tearDown(self):
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame_id)
        if self.app:
            self.apps.kill(self.app)

        self.marionette.execute_script(
                """SpecialPowers.setBoolPref("%s", false);""" % PREF_SYNTHETIC_EVENTS_OK,
                special_powers=True);

        if self.wifi:
            self.data_layer.disable_wifi()

        GaiaTestCase.tearDown(self)

