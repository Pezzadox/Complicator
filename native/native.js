/* The Complicator: the bits that only work inside the installed app.
 * On the website this does nothing. In the app it routes the "buzz on correct answers"
 * setting through the phone's own haptics, because iPhones ignore navigator.vibrate.
 */
(function () {
  'use strict';
  var cap = window.Capacitor;
  if (!cap || !cap.isNativePlatform || !cap.isNativePlatform()) return;
  function plugin(name) { try { return cap.Plugins[name] || (cap.registerPlugin && cap.registerPlugin(name)); } catch (e) { return null; } }
  var haptics = plugin('Haptics');
  if (!haptics) return;
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
  var splash = plugin('SplashScreen');
  if (splash) window.addEventListener('load', function () { try { splash.hide(); } catch (e) {} });
})();
