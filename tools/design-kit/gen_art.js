const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const OUT = path.join(__dirname, 'art');
fs.mkdirSync(OUT, { recursive: true });

// ---- bg_hero: title/closing — deep black with strong red glow right, faint blue, vignette
const bgHero = `
<svg width="2560" height="1440" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="red1" cx="0.79" cy="0.44" r="0.42">
      <stop offset="0%" stop-color="#C8102E" stop-opacity="0.52"/>
      <stop offset="45%" stop-color="#C8102E" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#C8102E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="red2" cx="0.05" cy="1.05" r="0.5">
      <stop offset="0%" stop-color="#7A0A1E" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="#7A0A1E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="blue1" cx="0.55" cy="0.12" r="0.4">
      <stop offset="0%" stop-color="#2EA8E0" stop-opacity="0.07"/>
      <stop offset="100%" stop-color="#2EA8E0" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vig" cx="0.5" cy="0.5" r="0.75">
      <stop offset="55%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.55"/>
    </radialGradient>
  </defs>
  <rect width="2560" height="1440" fill="#0A0C11"/>
  <rect width="2560" height="1440" fill="url(#red1)"/>
  <rect width="2560" height="1440" fill="url(#red2)"/>
  <rect width="2560" height="1440" fill="url(#blue1)"/>
  <rect width="2560" height="1440" fill="url(#vig)"/>
</svg>`;

// ---- bg_dark: content slides — subtle version
const bgDark = `
<svg width="2560" height="1440" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="red1" cx="0.92" cy="-0.08" r="0.55">
      <stop offset="0%" stop-color="#C8102E" stop-opacity="0.20"/>
      <stop offset="60%" stop-color="#C8102E" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#C8102E" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="blue1" cx="0.02" cy="1.05" r="0.45">
      <stop offset="0%" stop-color="#2EA8E0" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#2EA8E0" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vig" cx="0.5" cy="0.5" r="0.78">
      <stop offset="60%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.45"/>
    </radialGradient>
  </defs>
  <rect width="2560" height="1440" fill="#0A0C11"/>
  <rect width="2560" height="1440" fill="url(#red1)"/>
  <rect width="2560" height="1440" fill="url(#blue1)"/>
  <rect width="2560" height="1440" fill="url(#vig)"/>
</svg>`;

// ---- ring: glowing color-timer ring (transparent), blue core
const ring = `
<svg width="1400" height="1400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glowR" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="26"/>
    </filter>
    <filter id="glowB" x="-120%" y="-120%" width="340%" height="340%">
      <feGaussianBlur stdDeviation="20"/>
    </filter>
  </defs>
  <circle cx="700" cy="700" r="640" fill="none" stroke="#232A38" stroke-width="2"/>
  <circle cx="700" cy="700" r="480" fill="none" stroke="#39415A" stroke-width="2.5"/>
  <circle cx="700" cy="700" r="330" fill="none" stroke="#C8102E" stroke-width="26" filter="url(#glowR)" opacity="0.85"/>
  <circle cx="700" cy="700" r="330" fill="none" stroke="#E8354F" stroke-width="7"/>
  <circle cx="700" cy="700" r="46" fill="#2EA8E0" filter="url(#glowB)" opacity="0.9"/>
  <circle cx="700" cy="700" r="26" fill="#9FDCF5"/>
</svg>`;

// ---- beam: thin diagonal light streak (transparent) for title accent
const beam = `
<svg width="2000" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="b" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#C8102E" stop-opacity="0"/>
      <stop offset="35%" stop-color="#E8354F" stop-opacity="0.85"/>
      <stop offset="50%" stop-color="#FFD9E0" stop-opacity="1"/>
      <stop offset="65%" stop-color="#E8354F" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#C8102E" stop-opacity="0"/>
    </linearGradient>
    <filter id="soft" x="-20%" y="-300%" width="140%" height="700%">
      <feGaussianBlur stdDeviation="14"/>
    </filter>
  </defs>
  <rect x="0" y="138" width="2000" height="24" fill="url(#b)" filter="url(#soft)"/>
  <rect x="0" y="146" width="2000" height="7" fill="url(#b)"/>
</svg>`;

(async () => {
  await sharp(Buffer.from(bgHero)).png().toFile(path.join(OUT, 'bg_hero.png'));
  await sharp(Buffer.from(bgDark)).png().toFile(path.join(OUT, 'bg_dark.png'));
  await sharp(Buffer.from(ring)).png().toFile(path.join(OUT, 'ring.png'));
  await sharp(Buffer.from(beam)).png().toFile(path.join(OUT, 'beam.png'));
  console.log('art done');
})();
