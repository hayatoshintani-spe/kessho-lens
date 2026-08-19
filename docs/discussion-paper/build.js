const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LineRuleType,
} = require("docx");
const fs = require("fs");
const C = require("./content");

const FONT = { name: "Yu Gothic", eastAsia: "Yu Gothic", ascii: "Yu Gothic", hAnsi: "Yu Gothic", cs: "Yu Gothic" };
const NAVY = "1F3864", GREY = "595959", RULE = "BFBFBF", TINT = "EEF2F9", ZEBRA = "F5F7FB";
const BODY = 17, SMALL = 16;                       // half-points (8.5pt / 8pt)
const L_BODY = 245, L_SMALL = 235, L_HEAD = 258;    // exact line heights (twips)
const CONTENT_W = 10206;
const COLS = [1250, 5556, 3400];

const style = (s) => ({
  bold: s === "bold" || s === "accentbold",
  color: s === "grey" ? GREY : (s === "accent" || s === "accentbold") ? NAVY : "000000",
});

const mk = (text, size, s) => new TextRun({ text, font: FONT, size, ...style(s) });

const para = (runs, o = {}) => new Paragraph({
  spacing: { before: o.before || 0, after: o.after === undefined ? 40 : o.after, line: o.line || L_BODY, lineRule: LineRuleType.EXACTLY },
  indent: o.indent,
  shading: o.fill ? { type: ShadingType.CLEAR, color: "auto", fill: o.fill } : undefined,
  border: o.border,
  children: runs,
});

const line = (color, size) => ({ style: BorderStyle.SINGLE, size, color, space: 2 });

function heading(text) {
  return para([mk(text, 18, "accentbold")], {
    before: 110, after: 40, line: L_HEAD,
    border: { bottom: line(RULE, 4) },
  });
}

function cell(children, width, fill) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined,
    margins: { top: 55, bottom: 55, left: 90, right: 90 },
    children,
  });
}

function buildTable(block) {
  const b = (sz) => ({ style: BorderStyle.SINGLE, size: sz, color: RULE });
  const head = new TableRow({
    tableHeader: true,
    children: block.head.map((h, i) =>
      cell([para([new TextRun({ text: h, font: FONT, size: SMALL, bold: true, color: "FFFFFF" })], { after: 0, line: L_SMALL })], COLS[i], NAVY)),
  });
  const rows = block.rows.map((r, ri) => new TableRow({
    children: r.map((txt, i) =>
      cell([para([mk(txt, SMALL, i === 0 ? "accentbold" : i === 2 ? "grey" : null)], { after: 0, line: L_SMALL })],
        COLS[i], ri % 2 === 0 ? ZEBRA : "FFFFFF")),
  }));
  return new Table({
    columnWidths: COLS,
    width: { size: CONTENT_W, type: WidthType.DXA },
    borders: { top: b(4), bottom: b(4), left: b(4), right: b(4), insideHorizontal: b(4), insideVertical: b(4) },
    rows: [head, ...rows],
  });
}

const children = [
  para([mk(C.title, 24, "accentbold")], { after: 40, line: 305 }),
  para([mk(C.subtitle, SMALL, "grey")], { after: 120, line: L_SMALL, border: { bottom: line(NAVY, 12) } }),
];

for (const sec of C.sections) {
  children.push(heading(sec.h));
  for (const blk of sec.blocks) {
    const size = blk.small ? SMALL : BODY;
    const ln = blk.small ? L_SMALL : L_BODY;
    if (blk.t === "p") {
      children.push(para(blk.runs.map(([t, s]) => mk(t, size, s)), { line: ln }));
    } else if (blk.t === "callout") {
      children.push(para(blk.runs.map(([t, s]) => mk(t, 18, s)), { line: 262, after: 60, fill: TINT }));
    } else if (blk.t === "ul") {
      for (const item of blk.items) {
        children.push(para([mk("・", SMALL), mk(item, SMALL)], {
          line: L_SMALL, after: 20, indent: { left: 200, hanging: 200 },
        }));
      }
    } else if (blk.t === "table") {
      children.push(buildTable(blk));
    }
  }
}
children[children.length - 1] = para(
  C.sections.at(-1).blocks.at(-1).runs.map(([t, s]) => mk(t, SMALL, s)), { line: L_SMALL, after: 0 });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 800, bottom: 700, left: 850, right: 850 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(process.argv[2] || "out.docx", b); console.log("wrote", process.argv[2]); });
