"""Builds the catalog: packages every theme and extension in src/, renders preview images,
computes SHA-256 checksums, and writes catalog.json. Run from the repo root:

    python3 tools/build_catalog.py
"""
import glob, hashlib, json, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CLASSIC = {"panel": "#F7F7F8F2", "panelText": "#43474E", "panelBorder": "#FFFFFFE6", "hover": "#FFFFFFFF",
           "accent": "#F5A623", "accentText": "#FFFFFF", "iconBadge": "#5D6169", "iconGlyph": "#FFFFFF",
           "circle": "#F8F8F9F2", "circleIcon": "#8E9299", "circleBorder": "#FFFFFF", "infoFooter": "#E6E7EAF5"}
DIN = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
SANS = "/System/Library/Fonts/Helvetica.ttc"


def rgba(h):
    h = h.lstrip("#")
    if len(h) == 6:
        h += "FF"
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def backdrop(w, h):
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(40 + 30 * t), int(60 - 20 * t), int(110 - 30 * t), 255))
    return img


def theme_preview(theme, path):
    c = {**CLASSIC, **theme.get("colors", {})}
    W, H = 500, 260
    img = backdrop(W, H)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    accent = rgba(c["accent"])
    # info bubble
    d.rounded_rectangle([40, 40, 190, 220], 10, fill=rgba(c["panel"]), outline=rgba(c["panelBorder"]))
    d.rounded_rectangle([40, 160, 190, 220], 10, fill=rgba(c["infoFooter"]))
    d.text((115, 62), theme.get("name", "Theme"), font=font(DIN, 20), fill=rgba(c["panelText"]), anchor="mm")
    d.line([(55, 80), (175, 80)], fill=rgba(c["panelText"])[:3] + (90,), width=1)
    d.polygon([(190, 112), (208, 120), (190, 128)], fill=rgba(c["panel"]))
    # root buttons
    for i in range(4):
        cy = 52 + i * 52
        sel = i == 1
        if sel:
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse([206, cy - 28, 262, cy + 28], fill=accent[:3] + (170,))
            layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
            d = ImageDraw.Draw(layer)
            d.ellipse([209, cy - 25, 259, cy + 25], outline=accent, width=2)
        d.ellipse([214, cy - 20, 254, cy + 20], fill=accent if sel else rgba(c["circle"]), outline=rgba(c["circleBorder"]))
        d.ellipse([228, cy - 6, 240, cy + 6], fill=rgba(c["accentText"] if sel else c["circleIcon"]))
    # column
    names = ["Favorites", "Applications", "Places"]
    for i, n in enumerate(names):
        y = 92 + i * 36
        sel = i == 0
        d.rounded_rectangle([280, y, 460, y + 30], 4, fill=accent if sel else rgba(c["panel"]),
                            outline=accent if sel else rgba(c["panelBorder"]))
        d.ellipse([287, y + 5, 307, y + 25], fill=rgba(c["accentText"] if sel else c["iconBadge"]))
        d.text((318, y + 16), n, font=font(DIN, 17), fill=rgba(c["accentText"] if sel else c["panelText"]), anchor="lm")
    d.polygon([(278, 107), (270, 102), (270, 112)], fill=accent)
    img.alpha_composite(layer)
    img.convert("RGB").save(path, optimize=True)


CAT = {"ext": "#FFBF00", "launcher": "#FFBF00", "item": "#FFBF00", "timer": "#FFBF00", "app": "#FFBF00",
       "control": "#FFAB19", "act": "#4C97FF", "looks": "#9966FF", "sense": "#5CB1D6", "op": "#59C059", "var": "#FF8C1A"}
LABEL = {"ext.started": "when extension starts", "launcher.opened": "when the launcher opens",
         "item.chosen": "when menu item {name} is chosen", "timer.every": "every {seconds} seconds",
         "app.launched": "when app {app} opens", "app.quit": "when app {app} quits",
         "looks.message": "show message …", "looks.gauge": "set gauge {name} …", "looks.theme": "switch theme to {theme}",
         "var.set": "set [name] to …", "var.change": "change [name] by …", "control.if": "if … then",
         "control.repeat": "repeat … times", "act.openApp": "open app {app}", "act.openURL": "open website …"}


def label(block):
    text = LABEL.get(block["op"], block["op"])
    for k, v in block.get("inputs", {}).items():
        text = text.replace("{%s}" % k, v.get("fields", {}).get("value", "…") if v.get("op") == "literal" else "…")
    for k, v in block.get("fields", {}).items():
        text = text.replace("[%s]" % k, v)
    return text


def extension_preview(manifest, path):
    W, H = 500, 260
    img = backdrop(W, H)
    d = ImageDraw.Draw(img)
    f = font(SANS, 15)
    scripts = manifest.get("provides", {}).get("scripts", [])
    x, y = 30, 26
    for s in scripts[:2]:
        blocks = [s["trigger"]] + s.get("steps", [])[:3]
        for i, b in enumerate(blocks):
            col = rgba(CAT.get(b["op"].split(".")[0], "#888888"))
            text = label(b)
            w = int(d.textlength(text, font=f)) + 28
            top = y + (8 if i == 0 else 0)
            if i == 0:
                d.ellipse([x, y, x + 90, y + 24], fill=col)
            d.rounded_rectangle([x, top, x + w, y + 36], 5, fill=col)
            d.text((x + 12, (top + y + 36) / 2), text, font=f, fill=(255, 255, 255, 255), anchor="lm")
            y += 38
        y += 14
        if y > H - 60:
            break
    if not scripts:
        d.text((W / 2, H / 2), manifest["name"], font=font(DIN, 34), fill=(255, 255, 255, 255), anchor="mm")
    img.convert("RGB").save(path, optimize=True)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


items = []
os.makedirs("packages/themes", exist_ok=True)
for src in sorted(glob.glob("src/themes/*.json")):
    tid = os.path.splitext(os.path.basename(src))[0]
    theme = json.load(open(src))
    pkg = f"packages/themes/{tid}.json"
    shutil.copyfile(src, pkg)
    prev = f"previews/{tid}.png"
    theme_preview(theme, prev)
    items.append({"id": tid, "type": "theme", "name": theme.get("name", tid), "author": theme.get("author", "AINCRAD"),
                  "version": str(theme.get("version", "1.0")), "description": theme.get("description"),
                  "preview": prev, "package": pkg, "sha256": sha(pkg), "tags": ["theme"]})

for folder in sorted(glob.glob("src/extensions/*/")):
    manifest = json.load(open(os.path.join(folder, "extension.json")))
    eid = manifest["id"]
    pkg = f"packages/{eid}.aincrad"
    if os.path.exists(pkg):
        os.remove(pkg)
    subprocess.run(["/usr/bin/ditto", "-c", "-k", "--norsrc", "--keepParent", folder.rstrip("/"), pkg], check=True)
    prev = f"previews/{eid}.png"
    extension_preview(manifest, prev)
    items.append({"id": eid, "type": "extension", "name": manifest["name"], "author": manifest.get("author"),
                  "version": manifest["version"], "description": manifest.get("description"),
                  "preview": prev, "package": pkg, "sha256": sha(pkg),
                  "permissions": manifest.get("permissions", []), "tags": ["extension"]})

catalog = {"schemaVersion": 1, "name": "AINCRAD Community Catalog",
           "description": "Themes and block extensions for AINCRAD.", "items": items}
json.dump(catalog, open("catalog.json", "w"), indent=2)
print(f"catalog.json: {len(items)} items ({sum(i['type'] == 'theme' for i in items)} themes, "
      f"{sum(i['type'] == 'extension' for i in items)} extensions)")
