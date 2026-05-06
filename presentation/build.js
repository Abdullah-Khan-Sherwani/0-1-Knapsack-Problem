// Build the 0/1 Knapsack presentation deck from 15 HTML slide files.
const path = require('path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx.js');

async function build() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.title  = '0/1 Knapsack — Empirical Comparison of Six Algorithms';
    pptx.author = 'Anas Tabba, Abdullah Khan Sherwani, Zuhair Merchant, Raahin Raajiudin';

    const slidesDir = path.join(__dirname, 'slides');
    const total = 15;

    for (let i = 1; i <= total; i++) {
        const file = path.join(slidesDir, `slide${String(i).padStart(2, '0')}.html`);
        process.stdout.write(`  [${i}/${total}] ${path.basename(file)} ... `);
        await html2pptx(file, pptx);
        process.stdout.write('ok\n');
    }

    const out = path.join(__dirname, 'knapsack_presentation.pptx');
    await pptx.writeFile({ fileName: out });
    console.log(`\nSaved: ${out}`);
}

build().catch(err => { console.error(err); process.exit(1); });
