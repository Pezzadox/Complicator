/* The Complicator: the bits that only work inside the installed app.
 * On the website this does nothing. In the app it routes the "buzz on correct answers"
 * setting through the phone's own haptics, because iPhones ignore navigator.vibrate,
 * and on Android it shows one banner advert at the bottom of the screen.
 */
(function () {
  'use strict';
  var cap = window.Capacitor;
  if (!cap || !cap.isNativePlatform || !cap.isNativePlatform()) return;
  function plugin(name) { try { return cap.Plugins[name] || (cap.registerPlugin && cap.registerPlugin(name)); } catch (e) { return null; } }

  var haptics = plugin('Haptics');
  if (haptics) {
    // A short pattern is a light tap, a longer one a success buzz.
    navigator.vibrate = function (p) {
      try {
        var total = Array.isArray(p) ? p.reduce(function (a, b) { return a + b; }, 0) : (p || 0);
        if (total <= 0) return true;
        if (total < 40) haptics.impact({ style: 'LIGHT' });
        else if (total < 120) haptics.impact({ style: 'MEDIUM' });
        else haptics.notification({ type: 'SUCCESS' });
      } catch (e) {}
      return true;
    };
  }
  var splash = plugin('SplashScreen');
  if (splash) window.addEventListener('load', function () { try { splash.hide(); } catch (e) {} });

  /* The banner advert. Android only, and only when the release was built with an ad unit id.
   * One still banner under the keypad: no pop-ups, no video, nothing between puzzles.
   * It goes away in Focus view, and the page keeps clear of it through the --ad CSS variable. */
  var ads = window.COMPLICATOR_ADS || {};
  var admob = ads.banner && cap.getPlatform && cap.getPlatform() === 'android' ? plugin('AdMob') : null;
  if (!admob) return;

  var root = document.documentElement, shown = false, hidden = false, height = 0;
  function space() { root.style.setProperty('--ad', (shown && !hidden ? height : 0) + 'px'); }
  function inFocus() { var app = document.querySelector('.app'); return !!app && app.classList.contains('focus'); }
  function follow() {
    if (!shown) return;
    var want = inFocus();
    if (want === hidden) return;
    hidden = want;
    try { (hidden ? admob.hideBanner() : admob.resumeBanner()).catch(function () {}); } catch (e) {}
    space();
  }

  admob.addListener('bannerAdSizeChanged', function (size) { height = (size && size.height) || 0; space(); });
  admob.addListener('bannerAdLoaded', function () { shown = true; space(); follow(); });
  admob.addListener('bannerAdFailedToLoad', function () { shown = false; space(); });

  function consent() {
    // Asks Google's consent service whether this person must be shown a choice first (UK, EEA and others).
    return admob.requestConsentInfo().then(function (info) {
      if (info && info.privacyOptionsRequirementStatus === 'REQUIRED') choicesRow();
      if (info && info.isConsentFormAvailable && info.status === 'REQUIRED') return admob.showConsentForm();
      return info;
    }).catch(function () { return null; });
  }

  // Where consent applies, people must be able to change their mind: a row in "Make it yours".
  function choicesRow() {
    var done = document.getElementById('closeSettings');
    if (!done || document.getElementById('adChoices')) return;
    var row = document.createElement('div'); row.className = 'row';
    var text = document.createElement('div'), lbl = document.createElement('div'), sub = document.createElement('div');
    lbl.className = 'lbl'; lbl.textContent = 'Advert choices';
    sub.className = 'sub'; sub.textContent = 'Change what the banner advert may use';
    text.appendChild(lbl); text.appendChild(sub);
    var btn = document.createElement('button');
    btn.className = 'act'; btn.id = 'adChoices'; btn.type = 'button'; btn.textContent = 'Change'; btn.style.padding = '0 14px';
    btn.onclick = function () { try { admob.showPrivacyOptionsForm().catch(function () {}); } catch (e) {} };
    row.appendChild(text); row.appendChild(btn);
    done.parentNode.insertBefore(row, done);
  }

  admob.initialize({ maxAdContentRating: 'General' })
    .then(consent)
    .then(function (info) {
      if (info && info.canRequestAds === false) return;
      return admob.showBanner({ adId: ads.banner, adSize: 'ADAPTIVE_BANNER', position: 'BOTTOM_CENTER', margin: 0 });
    })
    .catch(function () {});

  var app = document.querySelector('.app');
  if (app && window.MutationObserver) new MutationObserver(follow).observe(app, { attributes: true, attributeFilter: ['class'] });
})();
