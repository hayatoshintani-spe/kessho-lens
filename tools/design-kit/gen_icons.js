const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const fa = require('react-icons/fa');

const OUT = path.join(__dirname, 'icons');
fs.mkdirSync(OUT, { recursive: true });

const icons = [
  'FaGlasses', 'FaUsers', 'FaCogs', 'FaGlobeAsia', 'FaShieldAlt',
  'FaBell', 'FaCamera', 'FaRoute', 'FaExpandArrowsAlt',
  'FaBolt', 'FaGem', 'FaStore', 'FaHashtag', 'FaYenSign', 'FaBullhorn',
  'FaCheck', 'FaLongArrowAltRight'
];

(async () => {
  for (const name of icons) {
    const Icon = fa[name];
    if (!Icon) { console.error('MISSING ICON:', name); process.exit(1); }
    const svg = ReactDOMServer.renderToStaticMarkup(
      React.createElement(Icon, { color: '#FFFFFF', size: 256 })
    );
    await sharp(Buffer.from(svg)).resize(256, 256, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png().toFile(path.join(OUT, `${name}.png`));
  }
  console.log('icons done:', icons.length);
})();
