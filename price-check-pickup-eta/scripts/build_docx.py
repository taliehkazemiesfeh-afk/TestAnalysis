"""Build the Pickup ETA report by cloning the UXR Product Report reference package.

The reference's styles, numbering, theme, header, footer and page setup are kept.
Only the body, the media, and the header/footer text are replaced.
"""
import os, re, shutil, subprocess
from xml.sax.saxutils import escape
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
# REF: the UXR Product Report template's assets/reference.docx, unzipped into a folder.
REF = os.environ.get("UXR_REFERENCE_DIR", os.path.join(HERE, "reference_unzipped"))
PKG = os.path.join(HERE, "pkg")
CHARTS = os.path.join(HERE, "..", "charts")
OUT = os.path.join(HERE, "..", "report", "Pickup_ETA_Copy_UXR_Report.docx")

shutil.rmtree(PKG, ignore_errors=True)
shutil.copytree(REF, PKG)
for f in os.listdir(os.path.join(PKG, "word", "media")):
    os.remove(os.path.join(PKG, "word", "media", f))

# ---------------------------------------------------------------- helpers
def t(s):
    return f'<w:t xml:space="preserve">{escape(s)}</w:t>'

def rpr(color="515c56", sz=19, b=False, i=False, font="Arial"):
    bb = '<w:b w:val="1"/><w:bCs w:val="1"/>' if b else '<w:b w:val="0"/><w:bCs w:val="0"/>'
    ii = '<w:i/>' if i else ''
    return (f'<w:rPr><w:rFonts w:ascii="{font}" w:cs="{font}" w:eastAsia="{font}" w:hAnsi="{font}"/>'
            f'{bb}{ii}<w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:rtl w:val="0"/></w:rPr>')

GREEN, RED, BLUE, INK, INK2, MUTED = "0ca30c", "d03b3b", "1c5cab", "17201c", "515c56", "6f7a74"

def runs(parts, sz=19, base=INK2):
    """parts: str or list of (text, kind). kind in n|b|g|r|blue|i"""
    if isinstance(parts, str):
        parts = [(parts, "n")]
    out = []
    for txt, k in parts:
        if k == "n":
            out.append(f'<w:r>{rpr(base, sz)}{t(txt)}</w:r>')
        elif k == "b":
            out.append(f'<w:r>{rpr(INK, sz, b=True)}{t(txt)}</w:r>')
        elif k == "g":
            out.append(f'<w:r>{rpr(GREEN, sz, b=True, font="Arial Unicode MS")}{t(txt)}</w:r>')
        elif k == "r":
            out.append(f'<w:r>{rpr(RED, sz, b=True, font="Arial Unicode MS")}{t(txt)}</w:r>')
        elif k == "blue":
            out.append(f'<w:r>{rpr(BLUE, sz, b=True)}{t(txt)}</w:r>')
        elif k == "i":
            out.append(f'<w:r>{rpr(base, sz, i=True)}{t(txt)}</w:r>')
    return "".join(out)

def p(inner, after=80, before=0, line=269, jc=None, extra=""):
    j = f'<w:jc w:val="{jc}"/>' if jc else ""
    return (f'<w:p><w:pPr>{extra}<w:spacing w:after="{after}" w:before="{before}" w:line="{line}" '
            f'w:lineRule="auto"/>{j}<w:rPr/></w:pPr>{inner}</w:p>')

def title(s):
    return (f'<w:p><w:pPr><w:pStyle w:val="Title"/><w:spacing w:after="40" w:before="280" w:line="259" '
            f'w:lineRule="auto"/><w:rPr/></w:pPr><w:r>{rpr(INK, 54, b=True)}{t(s)}</w:r></w:p>')

def subtitle(s):
    return (f'<w:p><w:pPr><w:pStyle w:val="Subtitle"/><w:spacing w:after="60" w:before="0" w:line="259" '
            f'w:lineRule="auto"/><w:rPr/></w:pPr><w:r>{rpr(BLUE, 30, b=True)}{t(s)}</w:r></w:p>')

def meta(s):
    return p(f'<w:r>{rpr(MUTED, 17)}{t(s)}</w:r>', after=180, line=259)

def empty():
    return '<w:p><w:pPr><w:rPr/></w:pPr></w:p>'

def pagebreak():
    return '<w:p><w:pPr><w:rPr/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>'

def h1(num, s, newpage=False):
    pb = '<w:pageBreakBefore/>' if newpage else ''
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:keepNext/>{pb}</w:pPr><w:r><w:rPr><w:b/><w:color w:val="1C5CAB"/></w:rPr>'
            f'<w:t>{num}</w:t></w:r><w:r><w:rPr><w:b/></w:rPr>{t("  " + s)}</w:r></w:p>')

def rq_label(s):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading3"/><w:keepNext/><w:spacing w:after="40" w:before="160" w:line="259" '
            f'w:lineRule="auto"/><w:rPr/></w:pPr><w:r>{rpr(BLUE, 16, b=True)}{t(s)}</w:r></w:p>')

def rq_question(s):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:keepNext/><w:spacing w:after="60" w:before="0" w:line="259" '
            f'w:lineRule="auto"/><w:rPr/></w:pPr><w:r>{rpr(INK, 23, b=True)}{t(s)}</w:r></w:p>')

def answer(parts):
    return p(runs(parts, 19), after=80, line=269)

def body(parts, after=140, before=80):
    return p(runs(parts, 17), after=after, before=before, line=264)

def lead(parts):
    return p(runs(parts, 17), after=40, line=259, extra="<w:keepNext/>")

def finding_h2(s):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:keepNext/><w:spacing w:after="60" w:before="200" w:line="259" '
            f'w:lineRule="auto"/><w:rPr/></w:pPr><w:r>{rpr(INK, 25, b=True)}{t(s)}</w:r></w:p>')

def action_h2(s):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:keepNext/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" '
            f'w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/><w:b/><w:color w:val="202F2B"/><w:sz w:val="22"/>'
            f'</w:rPr>{t(s)}</w:r></w:p>')

def h3(s):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading3"/><w:keepNext/><w:spacing w:after="40" w:before="120" w:line="259" '
            f'w:lineRule="auto"/><w:rPr/></w:pPr><w:r>{rpr(INK, 19, b=True)}{t(s)}</w:r></w:p>')

def bullet(parts, sz=17):
    return (f'<w:p><w:pPr><w:pStyle w:val="ListBullet"/><w:spacing w:after="40" w:before="0"/></w:pPr>'
            f'{runs(parts, sz)}</w:p>')

def caption(s):
    return p(f'<w:r>{rpr(MUTED, 14)}{t(s)}</w:r>', after=120, line=259, jc="center")

def italic_note(s):
    return (f'<w:p><w:pPr><w:spacing w:before="80"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:i/>'
            f'<w:color w:val="525E58"/><w:sz w:val="18"/></w:rPr>{t(s)}</w:r></w:p>')

def fa(s, sz=19, color=INK, jc="right", after=40):
    """A Persian (RTL) paragraph."""
    return (f'<w:p><w:pPr><w:bidi/><w:spacing w:after="{after}" w:before="20" w:line="259" w:lineRule="auto"/>'
            f'<w:jc w:val="{jc}"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:cs="Arial" w:eastAsia="Arial" '
            f'w:hAnsi="Arial"/><w:b/><w:bCs/><w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
            f'<w:rtl/><w:lang w:bidi="fa-IR"/></w:rPr>{t(s)}</w:r></w:p>')

# ---- images
RELS = []
_img = [0]
def image(fname, descr, width_in=6.4):
    _img[0] += 1
    n = _img[0]
    rid = f"rIdImg{n}"
    shutil.copy(os.path.join(CHARTS, fname), os.path.join(PKG, "word", "media", fname))
    RELS.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{fname}"/>')
    w, h = Image.open(os.path.join(CHARTS, fname)).size
    cx = int(width_in * 914400); cy = int(cx * h / w)
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:after="60" w:before="60" w:line="259" w:lineRule="auto"/><w:jc w:val="center"/><w:rPr/></w:pPr>'
            f'<w:r><w:rPr/><w:drawing><wp:inline distB="0" distT="0" distL="114300" distR="114300">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent b="0" l="0" r="0" t="0"/>'
            f'<wp:docPr id="{100+n}" name="{fname}" descr="{escape(descr)}"/><a:graphic><a:graphicData '
            f'uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr>'
            f'<pic:cNvPr id="0" name="{fname}" descr="{escape(descr)}"/><pic:cNvPicPr preferRelativeResize="0"/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:srcRect b="0" l="0" r="0" t="0"/><a:stretch><a:fillRect/>'
            f'</a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"/><a:ln/></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline>'
            f'</w:drawing></w:r></w:p>')

# ---- tables
BOX = ('<w:tcBorders><w:top w:color="dde2de" w:space="0" w:sz="5" w:val="single"/><w:left w:color="dde2de" '
       'w:space="0" w:sz="5" w:val="single"/><w:bottom w:color="dde2de" w:space="0" w:sz="5" w:val="single"/>'
       '<w:right w:color="dde2de" w:space="0" w:sz="5" w:val="single"/></w:tcBorders>')

def grid(widths):
    g = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    return f'<w:tblGrid>{g}</w:tblGrid>'

def tiles(items, style="Table10", fill="f7f9f7", big=24):
    """items: list of (big_text, kind, small_text); kind n|g|r|blue"""
    n = len(items); w = 10239 // n
    cells = []
    for big_t, kind, small in items:
        color = {"n": INK, "g": GREEN, "r": RED, "blue": BLUE}[kind]
        font = "Arial Unicode MS" if "→" in big_t else "Arial"
        cells.append(
            f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{BOX}<w:shd w:fill="{fill}" w:val="clear"/><w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:after="20" w:before="60" w:line="259" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>'
            f'<w:r>{rpr(color, big, b=True, font=font)}{t(big_t)}</w:r></w:p>'
            f'<w:p><w:pPr><w:spacing w:after="60" w:before="0" w:line="259" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>'
            f'<w:r>{rpr(MUTED, 14)}{t(small)}</w:r></w:p></w:tc>')
    return (f'<w:tbl><w:tblPr><w:tblStyle w:val="{style}"/><w:tblW w:w="{w*n}" w:type="dxa"/><w:jc w:val="center"/>'
            f'<w:tblLayout w:type="fixed"/><w:tblLook w:val="0400"/></w:tblPr>{grid([w]*n)}'
            f'<w:tr><w:trPr><w:cantSplit/></w:trPr>{"".join(cells)}</w:tr></w:tbl>')

def metrics_table(items):
    w = 3413
    cells = []
    for direction, name, why in items:
        color = BLUE if direction == "DECREASING" else GREEN
        cells.append(
            f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{BOX}<w:shd w:fill="f7f9f7" w:val="clear"/><w:vAlign w:val="top"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:after="40" w:before="40" w:line="259" w:lineRule="auto"/></w:pPr><w:r>{rpr(color, 15, b=True)}{t(direction)}</w:r></w:p>'
            f'<w:p><w:pPr><w:spacing w:after="60" w:before="0" w:line="259" w:lineRule="auto"/></w:pPr><w:r>{rpr(INK, 18, b=True)}{t(name)}</w:r></w:p>'
            f'<w:p><w:pPr><w:spacing w:after="60" w:before="0" w:line="252" w:lineRule="auto"/></w:pPr><w:r>{rpr(MUTED, 15)}{t(why)}</w:r></w:p></w:tc>')
    return (f'<w:tbl><w:tblPr><w:tblStyle w:val="Table6"/><w:tblW w:w="{w*3}" w:type="dxa"/><w:jc w:val="center"/>'
            f'<w:tblLayout w:type="fixed"/><w:tblLook w:val="0400"/></w:tblPr>{grid([w]*3)}'
            f'<w:tr><w:trPr><w:cantSplit/></w:trPr>{"".join(cells)}</w:tr></w:tbl>')

ACT_W = [2232, 2232, 4536, 1080]
CELL_MAR = ('<w:tcMar><w:top w:w="55" w:type="dxa"/><w:left w:w="65" w:type="dxa"/><w:bottom w:w="55" w:type="dxa"/>'
            '<w:right w:w="65" w:type="dxa"/></w:tcMar>')

def _cell(w, paras, hdr=False):
    if hdr:
        pr = (f'<w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders><w:bottom w:color="c3cbc6" w:space="0" w:sz="6" w:val="single"/>'
              f'</w:tcBorders><w:shd w:fill="eef1ee" w:val="clear"/>{CELL_MAR}<w:vAlign w:val="center"/></w:tcPr>')
    else:
        pr = (f'<w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders><w:bottom w:color="dde2de" w:space="0" w:sz="4" w:val="single"/>'
              f'</w:tcBorders>{CELL_MAR}<w:vAlign w:val="top"/></w:tcPr>')
    return f'<w:tc>{pr}{paras}</w:tc>'

def cp(text, b=False, color=None, sz=16):
    c = f'<w:color w:val="{color}"/>' if color else ""
    bb = "<w:b/>" if b else ""
    return (f'<w:p><w:pPr><w:spacing w:after="0" w:before="0" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:rPr>'
            f'<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>{bb}{c}<w:sz w:val="{sz}"/></w:rPr>'
            f'{t(text)}</w:r></w:p>')

def fa_cell(text):
    return (f'<w:p><w:pPr><w:bidi/><w:spacing w:after="20" w:before="40" w:line="240" w:lineRule="auto"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/><w:b/><w:bCs/>'
            f'<w:color w:val="1F5EAB"/><w:sz w:val="17"/><w:szCs w:val="17"/><w:rtl/><w:lang w:bidi="fa-IR"/></w:rPr>{t(text)}</w:r></w:p>')

def action_table(rows):
    hdr = "".join(_cell(w, cp(h, b=True, color="525E58"), hdr=True)
                  for w, h in zip(ACT_W, ["FINDING", "REASON", "CONCRETE ACTION", "OWNER"]))
    trs = [f'<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>{hdr}</w:tr>']
    for finding, reason, action, owner in rows:
        act = action if isinstance(action, list) else [action]
        act_xml = "".join(fa_cell(a[3:]) if a.startswith("FA:") else cp(a, b=True) for a in act)
        trs.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>'
                   + _cell(ACT_W[0], cp(finding, b=True)) + _cell(ACT_W[1], cp(reason))
                   + _cell(ACT_W[2], act_xml) + _cell(ACT_W[3], cp(owner, b=True, color="1F5EAB")) + '</w:tr>')
    return (f'<w:tbl><w:tblPr><w:tblStyle w:val="Table8"/><w:tblW w:w="{sum(ACT_W)}" w:type="dxa"/><w:jc w:val="center"/>'
            f'<w:tblLayout w:type="fixed"/><w:tblLook w:val="0400"/></w:tblPr>{grid(ACT_W)}{"".join(trs)}</w:tbl>')

def simple_table(headers, rows, widths, fa_col=None):
    hdr = "".join(_cell(w, cp(h, b=True, color="525E58"), hdr=True) for w, h in zip(widths, headers))
    trs = [f'<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>{hdr}</w:tr>']
    for r in rows:
        cells = []
        for ci, (w, v) in enumerate(zip(widths, r)):
            cells.append(_cell(w, fa_cell(v) if ci == fa_col else cp(v, b=(ci == 0))))
        trs.append(f'<w:tr><w:trPr><w:cantSplit/></w:trPr>{"".join(cells)}</w:tr>')
    return (f'<w:tbl><w:tblPr><w:tblStyle w:val="Table8"/><w:tblW w:w="{sum(widths)}" w:type="dxa"/><w:jc w:val="center"/>'
            f'<w:tblLayout w:type="fixed"/><w:tblLook w:val="0400"/></w:tblPr>{grid(widths)}{"".join(trs)}</w:tbl>')

# ---------------------------------------------------------------- content
B = []
A = B.append

A(title("Pickup ETA Copy"))
A(subtitle("A label helps. The meaning is still unclear."))
A(meta("Passenger research · Five-second test on Lyssna · 25 October 2026"))
A(tiles([("3,299", "n", "respondents"), ("9", "n", "ETA copies tested"),
         ("14.4%", "n", "read the ETA correctly"), ("11.7%", "n", "best copy, both answers right")],
        style="Table1", fill="fbfcfa", big=28))
A(empty())

# 01
A(h1("01", "Research Questions and Answers"))
A(rq_label("RQ 1"))
A(rq_question("Which ETA copy works best?"))
A(answer([("Six labeled copies tie at the top. ", "n"),
          ("V7 “Driver arrival: 3–5 min” ", "b"), ("is first: ", "n"), ("11.7%", "g"),
          (" got both questions right. The next five score 9.7–11.6%, and the gaps are not significant. "
           "Two copies with no label are clearly worse: V6 ", "n"), ("4.3%", "r"), (" and V3 ", "n"), ("3.3%", "r"), (".", "n")]))
A(image("c1_ranking.png", "Share of respondents who answered both questions correctly, by ETA copy, with 95% confidence intervals."))

A(rq_label("RQ 2"))
A(rq_question("Does a label in front of the time help?"))
A(answer([("Yes, on every measure. Both answers right: ", "n"), ("5.3% → 10.6–11.4%", "g"),
          (" when a label is added. Correct meaning: 10.3% → 15.5–16.8%. Correct time: 32.4% → 39.7–40.1%. "
           "All three gains are significant (p < .001).", "n")]))

A(rq_label("RQ 3"))
A(rq_question("Do the label words or the time format matter?"))
A(answer([("No. ", "b"), ("“Driver to origin” and “Driver arrival” score the same (10.6% vs 11.4% both right, p = .62). "
           "“<9 min”, “3–5 min” and “4 min” also score the same (8.5%, 8.6%, 9.7%, p = .64).", "n")]))
A(image("c5_heatmap.png", "Heatmap of both-answers-right rates by label (rows) and time format (columns)."))

A(rq_label("RQ 4"))
A(rq_question("What do passengers think the ETA means?"))
A(answer([("Most think it is the total wait from tapping Request. Only ", "n"), ("14.4%", "r"),
          (" chose the correct meaning (the wait at the origin after a car is found). ", "n"), ("20.6%", "r"),
          (" chose “the wait after tapping Request”, the top reading in every copy. 20.8% did not notice the line.", "n")]))
A(image("c2_q1_pooled.png", "What respondents thought the ETA meant, all nine copies combined."))

A(rq_label("RQ 5"))
A(rq_question("Do passengers remember the time?"))
A(answer([("About 4 in 10 do. Correct time by copy: ", "n"), ("29.7–42.1%", "b"),
          (". About 3 in 10 said “I don’t remember”. People who understood the meaning remembered the time twice as often: ", "n"),
          ("63.7% vs 32.7%", "b"), (".", "n")]))

# 02
A(h1("02", "Project Background"))
A(body("The ride-request screen shows a pickup ETA on the selected service card, for example “4 min until driver arrives”. "
       "The time means how long the passenger waits at the origin after a driver accepts the trip. It does not include the time "
       "to find a driver. We tested whether passengers read it this way, and which copy works best. We showed 9 versions of the "
       "screen in a five-second test on Lyssna: 3 labels (none, “Driver to origin”, “Driver arrival”) × 3 time formats "
       "(“<9 min”, “3–5 min”, “4 min”), with V1 using the wording “4 min until driver arrives”. 3,299 mobile users answered "
       "two questions. The results should guide which ETA copy to ship and what to test next."))
A(simple_table(["COPY", "SHOWN TEXT (PERSIAN)", "ENGLISH", "LABEL · FORMAT"], [
    ["V1", "۴ دقیقه تا رسیدن راننده", "4 min until driver arrives", "Suffix wording · 4 min"],
    ["V2", "راننده تا مبدأ: کمتر از ۹ دقیقه", "Driver to origin: <9 min", "Driver to origin · <9 min"],
    ["V3", "کمتر از ۹ دقیقه", "<9 min", "No label · <9 min"],
    ["V4", "رسیدن راننده: کمتر از ۹ دقیقه", "Driver arrival: <9 min", "Driver arrival · <9 min"],
    ["V5", "راننده تا مبدأ: ۳ تا ۵ دقیقه", "Driver to origin: 3–5 min", "Driver to origin · 3–5 min"],
    ["V6", "۳ تا ۵ دقیقه", "3–5 min", "No label · 3–5 min"],
    ["V7", "رسیدن راننده: ۳ تا ۵ دقیقه", "Driver arrival: 3–5 min", "Driver arrival · 3–5 min"],
    ["V8", "راننده تا مبدأ: ۴ دقیقه", "Driver to origin: 4 min", "Driver to origin · 4 min"],
    ["V9", "۴ دقیقه", "4 min", "No label · 4 min"],
], [1000, 3300, 3000, 2780], fa_col=1))

# 03
A(h1("03", "Metrics"))
A(metrics_table([
    ("DECREASING", "Passenger cancellations before pickup per 1,000 requests",
     "Main KR metric. Shows whether the shown ETA matches the wait passengers expect."),
    ("DECREASING", "Wait-time and “driver is late” support contacts per 1,000 completed rides",
     "Shows ETA confusion that turns into support cost."),
    ("INCREASING", "Ride requests per price-check screen view",
     "Guardrail. A longer or clearer ETA line must not lower the request rate."),
]))
A(p(runs([("Research signal: ", "b"), ("14.4% read the ETA correctly · best copy 11.7% both answers right.", "n")], 17),
    after=0, before=80, line=259))

# 04
A(h1("04", "Insights & Actions", newpage=True))
A(p(runs([("Cost guardrail: ", "b"), ("every action below is a copy, layout or test change on the existing price-check screen. "
                                        "No new spend and no new features are needed.", "n")], 19), after=80, before=80, line=259))
A(action_h2("Action principles"))
A(bullet("Always show a label in front of the ETA.", 19))
A(bullet("Fix the meaning first: tell passengers when the countdown starts.", 19))
A(bullet("Choose the time format by how accurate the estimate is, not by test score.", 19))
A(bullet("Test every new copy against V7 in the same five-second test before launch.", 19))

A(action_h2("4.1 Ship a labeled ETA"))
A(action_table([
    ("Remove copies without a label",
     "No-label copies are worst: 5.3% both right vs 10.6–11.4% with a label. V3 and V6 are significantly lower than every top copy.",
     "Drop V3, V6 and V9 from the candidates. Keep a label before the time on every service tab (car, motorbike, delivery).",
     "DESIGN"),
    ("Use V7 as the interim copy",
     "V7 “Driver arrival: 3–5 min” ranks first (11.7% both right, 42.1% correct time) but is tied with five other copies.",
     "If a launch decision is needed now, ship V7. Use V7 as the control copy in the next test.",
     "PRODUCT"),
    ("Pick the time format by accuracy",
     "Formats score the same (p = .64). 9–14% of people who saw “<9 min” remembered “5–10 min”.",
     "Show a range (“3–5 min”) when the estimate varies and one number (“4 min”) when it is reliable. Avoid “less than” formats.",
     "PRODUCT"),
]))

A(action_h2("4.2 Make the meaning clear"))
A(action_table([
    ("Say when the countdown starts",
     "Only 14.4% chose the correct meaning. “Wait after tapping Request” (20.6%) was the top reading in every copy. Today’s labels name the end point, not the start.",
     ["Write and test a label that names the start point. Main option:",
      "FA:بعد از قبول سفر، ۳ تا ۵ دقیقه تا رسیدن راننده",
      "(After the trip is accepted, 3–5 min until the driver arrives.) Short option:",
      "FA:رسیدن راننده پس از قبول: ۳ تا ۵ دقیقه"],
     "WRITING"),
    ("Show the two waits separately",
     "Passengers merge “finding a driver” and “driver on the way” into one wait.",
     ["If a matching-time estimate exists, test a two-part line:",
      "FA:یافتن راننده: ~۱ دقیقه · رسیدن راننده: ۳ تا ۵ دقیقه",
      "Check that the longer line does not lower noticing."],
     "DESIGN"),
    ("Decide which wait the screen shows",
     "Passengers expect the total wait. That is the question they bring to this screen.",
     "Test both directions: pickup-only ETA with a start anchor vs total wait “from now”. Choose with cancellation and complaint data.",
     "PRODUCT"),
]))

A(action_h2("4.3 Make the ETA easier to notice"))
A(action_table([
    ("Make the time stand out on the card",
     "20.8% did not notice the ETA and about 3 in 10 could not recall the time. People who understood the meaning remembered the time twice as often (63.7% vs 32.7%).",
     "On the selected card, set the time in bold and keep the label and the time on one line. Do not add icons or words that compete with it.",
     "DESIGN"),
]))

A(action_h2("4.4 Validate and monitor"))
A(action_table([
    ("Rerun the five-second test",
     "The start-anchored labels are not tested yet.",
     "Test 3–4 new copies plus V7 with the same two questions. About 370 people per copy can detect a rise from about 16% to 25% correct meaning.",
     "UX RESEARCH"),
    ("Track behaviour after launch",
     "The test measures understanding and recall, not behaviour.",
     "Compare cancellations before pickup, wait-time complaints and requests per view for 2 weeks before and after the change.",
     "PRODUCT"),
]))
A(italic_note("Priority order: label every ETA → name the start point → choose the format by accuracy → make the time stand out → validate and monitor."))

# 05
A(h1("05", "Detailed Findings"))
A(finding_h2("5.1 Six labeled copies tie at the top; two copies without a label fall behind"))
A(lead("We ranked copies by the share who got both questions right. Differences inside the top six are small and not significant."))
A(tiles([("11.7%", "g", "best copy · V7"), ("3.3%", "r", "worst copy · V3"), ("3.5x", "n", "gap between best and worst")]))
A(h3("What the tiers mean"))
A(bullet([("Top tier (V7, V1, V2, V4, V8, V5): ", "b"), ("no two copies differ significantly.", "n")]))
A(bullet([("Middle (V9 “4 min”): ", "b"), ("not clearly different from either group on both answers; lower than V7 and V8 on remembering the time.", "n")]))
A(bullet([("Bottom (V6 “3–5 min”, V3 “<9 min”): ", "b"), ("significantly lower than every top-tier copy.", "n")]))
A(caption("Both right = correct meaning and correct time · pairwise tests corrected for 36 comparisons (Holm)"))

A(finding_h2("5.2 Most passengers think the ETA is the total wait"))
A(lead("The correct meaning was only the 4th most common answer. The “total wait” reading beat it in every copy."))
A(image("c3_dumbbell.png", "Per copy: share choosing the correct meaning versus the total-wait reading."))
A(h3("Interpretation"))
A(body("The tested labels say where the driver is going (“to origin”, “arrival”). They do not say when the time starts. "
       "Passengers fill this gap with the moment they tap Request.", after=80, before=0))

A(finding_h2("5.3 A label lifts both understanding and recall"))
A(lead("Copies with a label beat copies without one on every measure (p < .001). The two labels score almost the same."))
A(image("c4_label_groups.png", "Correct meaning, correct time and both right, pooled by label group."))
A(bullet([("Correct meaning: ", "n"), ("10.3% → 15.5–16.8%", "g")]))
A(bullet([("Correct time: ", "n"), ("32.4% → 39.7–40.1%", "g")]))
A(bullet([("Both right: ", "n"), ("5.3% → 10.6–11.4%", "g")]))

A(finding_h2("5.4 The label words and the time format make no real difference"))
A(lead("Once a label is present, the exact words and the number format barely change the result."))
A(bullet("“Driver to origin” vs “Driver arrival”: 10.6% vs 11.4% both right (p = .62)."))
A(bullet("“<9 min” vs “3–5 min” vs “4 min”: 8.5%, 8.6%, 9.7% both right (p = .64)."))
A(bullet("“<9 min” is often stretched: 9–14% of people who saw it remembered “5–10 min”."))

A(finding_h2("5.5 About 3 in 10 cannot recall the time"))
A(lead("The correct time was the top answer in every copy except V9 (“4 min” with no label), where “don’t remember” won (32.8% vs 29.7%)."))
A(image("c6_q2_stack.png", "Per copy: correct time, wrong time and don't remember."))
A(h3("Understanding and recall go together"))
A(image("c7_recall_link.png", "Share remembering the correct time among people who did and did not understand the meaning."))
A(tiles([("37.2%", "n", "remembered the correct time"), ("30.7%", "n", "said “I don’t remember”"),
         ("2x", "n", "recall when the meaning was understood")]))

# 06
A(h1("06", "Methodology"))
A(body("Five-second test on Lyssna: each person saw one screen for 5 seconds, then answered what the time meant and what time was shown. "
       "Differences were checked with chi-square tests and pairwise tests.", after=80, before=40))

# 07
A(h1("07", "Sampling"))
A(tiles([("3,299", "n", "respondents · 25 Oct 2026"), ("95%", "n", "confidence level"),
         ("± 5.1%", "n", "margin of error per copy (± 1.7% overall)")]))
A(bullet("9 copies with 352–389 respondents each. Each person saw one copy only."))
A(bullet("Mobile devices only. The test and the screens were in Persian."))
A(p(runs("Source: Lyssna project “Price Check Pickup ETA”, tests Var 1–9.", 16, MUTED), after=0, before=80, line=259))

# ---------------------------------------------------------------- assemble
doc_path = os.path.join(PKG, "word", "document.xml")
x = open(doc_path, encoding="utf8").read()
head = x[:x.index("<w:body>") + 8]
sect = re.search(r"<w:sectPr>.*?</w:sectPr>", x[x.index("<w:body>"):], re.S).group(0)
open(doc_path, "w", encoding="utf8").write(head + "".join(B) + sect + "</w:body></w:document>")

rels_path = os.path.join(PKG, "word", "_rels", "document.xml.rels")
r = open(rels_path, encoding="utf8").read()
r = re.sub(r'<Relationship Id="[^"]+" Type="[^"]+/image" Target="media/[^"]+"/>', "", r)
r = r.replace("</Relationships>", "".join(RELS) + "</Relationships>")
open(rels_path, "w", encoding="utf8").write(r)

for fn, old, new in [("header1.xml", "INCENTIVE AUTOPAYMENT · UX RESEARCH REPORT", "PICKUP ETA COPY · UX RESEARCH REPORT"),
                     ("header1.xml", "DRIVER RESEARCH · SEP 2026", "PASSENGER RESEARCH · OCT 2026"),
                     ("footer1.xml", "September 2026", "October 2026")]:
    fp = os.path.join(PKG, "word", fn)
    s = open(fp, encoding="utf8").read()
    assert old in s, (fn, old)
    open(fp, "w", encoding="utf8").write(s.replace(old, new))

ct = os.path.join(PKG, "[Content_Types].xml")
s = open(ct, encoding="utf8").read()
if 'Extension="png"' not in s:
    s = s.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1)
open(ct, "w", encoding="utf8").write(s)

core = os.path.join(PKG, "docProps", "core.xml")
s = open(core, encoding="utf8").read()
s = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>Pickup ETA Copy · UX Research Report</dc:title>", s)
open(core, "w", encoding="utf8").write(s)

for junk in [".DS_Store"]:
    for root, _, files in os.walk(PKG):
        if junk in files:
            os.remove(os.path.join(root, junk))

if os.path.exists(OUT):
    os.remove(OUT)
subprocess.run(["zip", "-X", "-q", OUT, "[Content_Types].xml"], cwd=PKG, check=True)
subprocess.run(["zip", "-X", "-r", "-q", OUT, ".", "-x", "[Content_Types].xml"], cwd=PKG, check=True)
print("wrote", OUT)
