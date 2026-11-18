# The banner advert, tested against a stand-in for the phone: the app build is loaded in a
# browser with a fake Capacitor and a fake AdMob plugin that records what the app asks for.
import os, subprocess, sys
from playwright.sync_api import sync_playwright

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TEST_UNIT = 'ca-app-pub-3940256099942544/9214589741'  # Google's public test banner


def ok(c, m): print(('PASS ' if c else 'FAIL ') + m)


def build(banner):
    env = dict(os.environ); env.pop('ADMOB_BANNER_ID', None)
    if banner: env['ADMOB_BANNER_ID'] = banner
    subprocess.run(['node', 'tools/build-www.js'], cwd=root, env=env, check=True, stdout=subprocess.DEVNULL)


FAKE = """
(() => {
  const calls = [], listeners = {};
  const later = v => new Promise(r => setTimeout(() => r(v), 5));
  const AdMob = {
    initialize: o => { calls.push(['initialize', o]); return later(); },
    requestConsentInfo: () => { calls.push(['requestConsentInfo']); return later(window.__consent); },
    showConsentForm: () => { calls.push(['showConsentForm']); return later({ status: 'OBTAINED', canRequestAds: window.__afterForm }); },
    showPrivacyOptionsForm: () => { calls.push(['showPrivacyOptionsForm']); return later(); },
    showBanner: o => { calls.push(['showBanner', o]); setTimeout(() => { fire('bannerAdSizeChanged', { width: 390, height: 61 }); fire('bannerAdLoaded'); }, 5); return later(); },
    hideBanner: () => { calls.push(['hideBanner']); return later(); },
    resumeBanner: () => { calls.push(['resumeBanner']); return later(); },
    addListener: (n, f) => { (listeners[n] = listeners[n] || []).push(f); return later({ remove() {} }); },
  };
  function fire(n, d) { (listeners[n] || []).forEach(f => f(d)); }
  window.__calls = calls;
  window.Capacitor = { isNativePlatform: () => true, getPlatform: () => window.__platform, Plugins: { AdMob } };
})();
"""


def run(p, platform, consent, after_form=True):
    b = p.chromium.launch()
    pg = b.new_context(viewport={'width': 390, 'height': 844}).new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script(f"window.__platform={platform!r};window.__consent={consent};window.__afterForm={'true' if after_form else 'false'};" + FAKE)
    pg.goto('file://' + os.path.join(root, 'www', 'index.html')); pg.wait_for_timeout(500)
    return b, pg, errs


names = lambda pg: [c[0] for c in pg.evaluate('()=>window.__calls')]
pad = lambda pg: pg.evaluate("()=>getComputedStyle(document.documentElement).getPropertyValue('--ad').trim()")

with sync_playwright() as p:
    # 1. No ad unit id in the build: the app never touches the advert plugin.
    build('')
    b, pg, errs = run(p, 'android', "{status:'NOT_REQUIRED',canRequestAds:true}")
    ok(names(pg) == [] and not errs, 'no ad unit id: no advert calls at all')
    b.close()

    build(TEST_UNIT)
    # 2. Android, consent not needed: one adaptive banner at the bottom, page makes room.
    b, pg, errs = run(p, 'android', "{status:'NOT_REQUIRED',canRequestAds:true,privacyOptionsRequirementStatus:'NOT_REQUIRED'}")
    calls = pg.evaluate('()=>window.__calls')
    shown = [c for c in calls if c[0] == 'showBanner']
    ok(names(pg)[:3] == ['initialize', 'requestConsentInfo', 'showBanner'] and 'showConsentForm' not in names(pg), 'order: initialise, ask consent service, banner')
    ok(len(shown) == 1 and shown[0][1] == {'adId': TEST_UNIT, 'adSize': 'ADAPTIVE_BANNER', 'position': 'BOTTOM_CENTER', 'margin': 0}, 'exactly one bottom banner with the built-in unit id')
    ok(calls[0][1] == {'maxAdContentRating': 'General'}, 'adverts limited to general audiences')
    ok(pad(pg) == '61px', 'page keeps clear of the banner: --ad = ' + pad(pg))
    box = pg.evaluate("()=>{const a=document.getElementById('app'),k=document.getElementById('keys').getBoundingClientRect();return [k.bottom, innerHeight-61]}")
    ok(box[0] <= box[1] + 0.5, f'keypad ends above the banner ({box[0]:.0f} <= {box[1]:.0f})')
    ok(pg.query_selector('#adChoices') is None, 'no advert-choices row where consent does not apply')
    # Focus view hides it and gives the space back; leaving Focus view brings it back.
    pg.click('#aFocus'); pg.wait_for_timeout(100)
    ok(names(pg)[-1] == 'hideBanner' and pad(pg) == '0px', 'Focus view hides the banner')
    pg.click('#aFocus'); pg.wait_for_timeout(100)
    ok(names(pg)[-1] == 'resumeBanner' and pad(pg) == '61px', 'leaving Focus view brings it back')
    ok(not errs, 'no page errors' + (': ' + errs[0] if errs else ''))
    b.close()

    # 3. Consent required: the form comes before any advert, and the choice can be reopened.
    b, pg, errs = run(p, 'android', "{status:'REQUIRED',isConsentFormAvailable:true,canRequestAds:false,privacyOptionsRequirementStatus:'REQUIRED'}")
    n = names(pg)
    ok('showConsentForm' in n and n.index('showConsentForm') < n.index('showBanner'), 'consent form is shown before the banner')
    pg.click('#openSettings'); pg.click('#adChoices'); pg.wait_for_timeout(50)
    ok(names(pg)[-1] == 'showPrivacyOptionsForm', 'Make it yours → Advert choices reopens the choice')
    b.close()

    # 4. Consent service says adverts may not be requested: no banner.
    b, pg, errs = run(p, 'android', "{status:'REQUIRED',isConsentFormAvailable:true,canRequestAds:false}", after_form=False)
    ok('showBanner' not in names(pg) and pad(pg) in ('', '0px'), 'no banner when adverts may not be requested')
    b.close()

    # 5. iPhone build never shows adverts, even with an ad unit id.
    b, pg, errs = run(p, 'ios', "{status:'NOT_REQUIRED',canRequestAds:true}")
    ok(names(pg) == [] and not errs, 'iPhone: no advert calls')
    b.close()

build('')  # leave www/ as a normal build
