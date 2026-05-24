# van groot naar klein

Video compressor web app. Upload een `.mov` bestand (max 5 GB) en krijg een gecomprimeerde versie terug via de server.

## Installeren & starten

```bash
npm install
npm run dev
```

## Bouwen voor productie

```bash
npm run build
```

De `dist/` map kun je deployen op Vercel, Netlify, GitHub Pages, of Railway.

## Bestandsstructuur

```
├── index.html
├── main.jsx
├── van-groot-naar-klein.jsx   ← hoofdcomponent
├── vite.config.js
└── package.json
```

## Server

Uploads gaan naar: `https://egel-production.up.railway.app/upload`
