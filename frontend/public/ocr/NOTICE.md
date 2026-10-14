# Self-hosted OCR runtime

Tesseract.js 7.0.0 and tesseract.js-core 7.0.0, Apache-2.0. Copyright their respective contributors. License copies are included. These bundled distributions are unmodified.

English `4.0.0_best_int` trained data from `@tesseract.js-data/eng` 1.0.0, maintained by naptha/tessdata. The upstream trained-data repository is Apache-2.0; the npm package wrapper declares MIT. Data is an integerized Tesseract Best model. No medical training or medical OCR validation is implied.

Sources: https://github.com/naptha/tesseract.js, https://github.com/naptha/tesseract.js-core, https://github.com/naptha/tessdata, https://github.com/tesseract-ocr/tessdata_best.

Regenerate with `npm ci` followed by `node scripts/vendor-ocr.mjs` from `frontend`. The manifest records each distributed file's bytes and SHA256. OCR uses OEM 1; the baseline, SIMD and relaxed-SIMD LSTM runtimes are included. No remote OCR service or runtime CDN is used.
