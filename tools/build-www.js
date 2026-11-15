// Builds www/ (what goes inside the app) from the one index.html that also runs on the web.
// Fonts are bundled so the app works offline, and native.js is added for haptics.
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..'), www = path.join(root, 'www'), fonts = path.join(www, 'fonts');
fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(fonts, { recursive: true });

const faces = [
  ['Space Grotesk', 'space-grotesk', [500, 700]],
  ['JetBrains Mono', 'jetbrains-mono', [700, 800]],
  ['Atkinson Hyperlegible', 'atkinson-hyperlegible', [400, 700]],
];
let css = '';
for (const [family, pkg, weights] of faces) for (const w of weights) {
  const file = `${pkg}-latin-${w}-normal.woff2`;
  fs.copyFileSync(path.join(root, 'node_modules/@fontsource', pkg, 'files', file), path.join(fonts, file));
  css += `@font-face{font-family:'${family}';font-style:normal;font-weight:${w};font-display:swap;src:url(${file}) format('woff2')}\n`;
}
fs.writeFileSync(path.join(fonts, 'fonts.css'), css);

let html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const before = html;
html = html.replace(/<link rel="preconnect" href="https:\/\/fonts\.googleapis\.com">\s*/, '')
           .replace(/<link href="https:\/\/fonts\.googleapis\.com\/css2[^>]*>/, '<link rel="stylesheet" href="fonts/fonts.css">');
if (html === before || /fonts\.googleapis/.test(html)) throw new Error('Could not swap the Google Fonts link for the bundled fonts');
if (!html.includes('</body>')) throw new Error('index.html has no </body>');
html = html.replace('</body>', '<script src="native.js"></script>\n</body>');
fs.writeFileSync(path.join(www, 'index.html'), html);
fs.copyFileSync(path.join(root, 'native/native.js'), path.join(www, 'native.js'));
console.log('www/ built: index.html, native.js, ' + faces.reduce((n, f) => n + f[2].length, 0) + ' fonts');
