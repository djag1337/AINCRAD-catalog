"""Writes the AINCRAD plugin pack: extension folders in src/extensions (for the catalog) and, with
--app <AINCRAD repo>, the same folders in AINCRAD/Resources/Plugins (preinstalled with the app).
They're ordinary extension.json files; open any of them in the Extension Studio to see the blocks."""
import json, os, shutil, sys

def lit(v): return {"op": "literal", "fields": {"value": str(v)}}
def b(op, inputs=None, fields=None, body=None, else_=None):
    x = {"op": op, "inputs": {k: (v if isinstance(v, dict) else lit(v)) for k, v in (inputs or {}).items()},
         "fields": fields or {}}
    if body is not None: x["body"] = body
    if else_ is not None: x["elseBody"] = else_
    return x
def var(name): return b("var.get", fields={"name": name})
def reading(r): return b("sense.reading", fields={"reading": r})
def now(part): return b("sense.time", fields={"part": part})
def join(*parts):
    out = parts[0]
    for p in parts[1:]: out = b("op.join", {"a": out, "b": p})
    return out
def msg(text): return b("looks.message", {"text": text})
def script(trigger, *steps): return {"trigger": trigger, "steps": list(steps)}
def gauge_widget(ext, name, label, show="bar", width=260):
    return {"name": label, "widget": {"type": "stat", "width": width, "height": 70,
            "props": {"source": f"script:{ext}/{name}", "show": show, "label": name}}}
def item(name, icon, kind, target): return {"name": name, "icon": icon, "action": {"type": kind, "target": target}}
def pane(name, icon, ext): return item(name, icon, "url", "x-apple.systempreferences:" + ext)
def chosen(name): return b("item.chosen", {"name": name})
def noop(name, icon): return item(name, icon, "builtin", "none")

base = {"version": "1.0", "apiVersion": 1, "author": "AINCRAD", "permissions": []}
plugins = {}
def plugin(folder, ext_id, name, description, provides, permissions=None, files=None):
    plugins[folder] = ({**base, "id": ext_id, "name": name, "description": description,
                        "permissions": permissions or [], "provides": provides}, files or {})

# ---- Menus -------------------------------------------------------------------------------

plugin("settings-panes", "aincrad.settings-panes", "Settings Panes",
  "Jump straight to the System Settings page you want. Its menu appears under Command Center › Plugins.",
  {"menus": [{"id": "panes", "name": "Settings Panes", "items": [
    pane("Wi-Fi", "sf:wifi", "com.apple.wifi-settings-extension"),
    pane("Bluetooth", "sf:dot.radiowaves.left.and.right", "com.apple.BluetoothSettings"),
    pane("Network", "sf:network", "com.apple.Network-Settings.extension"),
    pane("Displays", "sf:display.2", "com.apple.Displays-Settings.extension"),
    pane("Sound", "sf:speaker.wave.2.fill", "com.apple.Sound-Settings.extension"),
    pane("Desktop & Dock", "sf:dock.rectangle", "com.apple.Desktop-Settings.extension"),
    pane("Wallpaper", "sf:photo.fill", "com.apple.Wallpaper-Settings.extension"),
    pane("Appearance", "sf:circle.lefthalf.filled", "com.apple.Appearance-Settings.extension"),
    pane("Keyboard", "sf:keyboard.fill", "com.apple.Keyboard-Settings.extension"),
    pane("Mouse", "sf:computermouse.fill", "com.apple.Mouse-Settings.extension"),
    pane("Notifications", "sf:bell.badge.fill", "com.apple.Notifications-Settings.extension"),
    pane("Privacy & Security", "sf:hand.raised.fill", "com.apple.settings.PrivacySecurity.extension"),
    pane("Accessibility", "sf:accessibility", "com.apple.Accessibility-Settings.extension"),
    pane("Storage", "sf:internaldrive.fill", "com.apple.settings.Storage"),
    pane("Software Update", "sf:arrow.triangle.2.circlepath", "com.apple.Software-Update-Settings.extension"),
  ]}]})

plugin("quick-folders", "aincrad.quick-folders", "Quick Folders",
  "Your everyday folders in one submenu: Home, Desktop, Documents, Downloads, iCloud Drive, Applications, Screenshots and the Trash.",
  {"menus": [{"id": "folders", "name": "Quick Folders", "items": [
    item("Home", "sf:house.fill", "open", "~"),
    item("Desktop", "sf:menubar.dock.rectangle", "open", "~/Desktop"),
    item("Documents", "sf:doc.fill", "open", "~/Documents"),
    item("Downloads", "sf:arrow.down.circle.fill", "open", "~/Downloads"),
    item("iCloud Drive", "sf:icloud.fill", "open", "~/Library/Mobile Documents/com~apple~CloudDocs"),
    item("Applications", "sf:square.grid.3x3.fill", "open", "/Applications"),
    item("Screenshot app", "sf:camera.viewfinder", "app", "/System/Applications/Utilities/Screenshot.app"),
    item("Trash", "sf:trash.fill", "open", "~/.Trash"),
  ]}]})

plugin("web-links", "aincrad.web-links", "Web Quick Links",
  "One-click sites: mail, calendar, drive, YouTube, Reddit, GitHub, ChatGPT, Claude, Twitch and Discord.",
  {"menus": [{"id": "links", "name": "Web Links", "items": [
    item("Gmail", "sf:envelope.fill", "url", "https://mail.google.com"),
    item("Calendar", "sf:calendar", "url", "https://calendar.google.com"),
    item("Drive", "sf:externaldrive.fill", "url", "https://drive.google.com"),
    item("YouTube", "sf:play.rectangle.fill", "url", "https://www.youtube.com"),
    item("Reddit", "sf:bubble.left.and.bubble.right.fill", "url", "https://www.reddit.com"),
    item("GitHub", "sf:chevron.left.forwardslash.chevron.right", "url", "https://github.com"),
    item("ChatGPT", "sf:sparkles", "url", "https://chatgpt.com"),
    item("Claude", "sf:sparkle", "url", "https://claude.ai"),
    item("Twitch", "sf:tv.fill", "url", "https://www.twitch.tv"),
    item("Discord", "sf:message.fill", "url", "https://discord.com/app"),
  ]}]})

plugin("dev-hub", "aincrad.dev-hub", "Developer Hub",
  "Tools and pages developers reach for: Terminal, Activity Monitor, Console, local servers, GitHub, Stack Overflow and Apple's docs.",
  {"menus": [{"id": "dev", "name": "Developer Hub", "items": [
    item("Terminal", "sf:terminal.fill", "app", "/System/Applications/Utilities/Terminal.app"),
    item("Activity Monitor", "sf:waveform.path.ecg", "app", "/System/Applications/Utilities/Activity Monitor.app"),
    item("Console", "sf:list.bullet.rectangle.fill", "app", "/System/Applications/Utilities/Console.app"),
    item("localhost:3000", "sf:server.rack", "url", "http://localhost:3000"),
    item("localhost:8080", "sf:server.rack", "url", "http://localhost:8080"),
    item("GitHub", "sf:chevron.left.forwardslash.chevron.right", "url", "https://github.com"),
    item("Stack Overflow", "sf:questionmark.bubble.fill", "url", "https://stackoverflow.com"),
    item("Apple Developer Docs", "sf:book.fill", "url", "https://developer.apple.com/documentation"),
  ]}]})

plugin("media-hub", "aincrad.media-hub", "Media Hub",
  "Music and video in one place: the Music app, Spotify, YouTube Music, SoundCloud, Twitch and Crunchyroll.",
  {"menus": [{"id": "media", "name": "Media Hub", "items": [
    item("Music", "sf:music.note", "app", "/System/Applications/Music.app"),
    item("Spotify (web)", "sf:music.note.list", "url", "https://open.spotify.com"),
    item("YouTube Music", "sf:play.circle.fill", "url", "https://music.youtube.com"),
    item("SoundCloud", "sf:cloud.fill", "url", "https://soundcloud.com"),
    item("Twitch", "sf:tv.fill", "url", "https://www.twitch.tv"),
    item("Crunchyroll", "sf:film.fill", "url", "https://www.crunchyroll.com"),
  ]}]})

# ---- Gauges and stats --------------------------------------------------------------------

E = "aincrad.player-stats"
plugin("player-stats", E, "Player Stats",
  "MP (free memory) and Stamina (free disk) gauges to go with System HP, updated every 10 seconds. Add them from the Widgets library.",
  {"scripts": [script(b("timer.every", {"seconds": 10}),
      b("var.set", {"value": b("op.sub", {"a": 100, "b": reading("memory")})}, {"name": "mp"}),
      b("looks.gauge", {"name": "MP", "text": join(var("mp"), " / 100"), "percent": var("mp")}),
      b("var.set", {"value": b("op.sub", {"a": 100, "b": reading("disk")})}, {"name": "stamina"}),
      b("looks.gauge", {"name": "Stamina", "text": join(var("stamina"), "% free"), "percent": var("stamina")}))],
   "widgets": [gauge_widget(E, "MP", "MP gauge (memory)"), gauge_widget(E, "Stamina", "Stamina gauge (disk)")]})

E = "aincrad.floor-counter"
plugin("floor-counter", E, "Floor Counter",
  "Every hour your Mac stays up clears a floor of Aincrad. A gauge shows the floor out of 100.",
  {"scripts": [script(b("timer.every", {"seconds": 60}),
      b("var.set", {"value": b("op.add", {"a": reading("uptime hours"), "b": 1})}, {"name": "floor"}),
      b("control.if", {"condition": b("op.gt", {"a": var("floor"), "b": 100})}, body=[b("var.set", {"value": 100}, {"name": "floor"})]),
      b("looks.gauge", {"name": "Floor", "text": join("Floor ", var("floor"), " / 100"), "percent": var("floor")}))],
   "widgets": [gauge_widget(E, "Floor", "Aincrad floor")]})

# ---- Alerts ------------------------------------------------------------------------------

plugin("low-hp", "aincrad.low-hp", "Low HP Warning",
  "Warns once when the battery drops below 20% (does nothing on Macs without a battery).",
  {"scripts": [script(b("timer.every", {"seconds": 60}),
      b("var.set", {"value": reading("battery")}, {"name": "bat"}),
      b("control.if", {"condition": b("op.and", {"a": b("op.gt", {"a": var("bat"), "b": 0}),
                                                 "b": b("op.lt", {"a": var("bat"), "b": 20})})}, body=[
          b("control.if", {"condition": b("op.not", {"a": b("op.eq", {"a": var("warned"), "b": 1})})}, body=[
              msg(join("HP low: ", var("bat"), "%. Plug in to recover!")),
              b("var.set", {"value": 1}, {"name": "warned"})])]),
      b("control.if", {"condition": b("op.gt", {"a": var("bat"), "b": 30})}, body=[b("var.set", {"value": 0}, {"name": "warned"})]))]})

plugin("storage-alert", "aincrad.storage-alert", "Storage Alert",
  "Warns once when your disk is more than 90% full, and again if it fills up after you clear space.",
  {"scripts": [script(b("timer.every", {"seconds": 600}),
      b("var.set", {"value": reading("disk")}, {"name": "disk"}),
      b("control.ifElse", {"condition": b("op.gt", {"a": var("disk"), "b": 90})}, body=[
          b("control.if", {"condition": b("op.not", {"a": b("op.eq", {"a": var("warned"), "b": 1})})}, body=[
              msg(join("Inventory almost full: disk ", var("disk"), "% used.")),
              b("var.set", {"value": 1}, {"name": "warned"})])],
        else_=[b("var.set", {"value": 0}, {"name": "warned"})]))]})

plugin("rest-point", "aincrad.rest-point", "Rest Point",
  "A break reminder every 50 minutes: stand up, stretch, drink some water.",
  {"scripts": [script(b("timer.every", {"seconds": 3000}),
      msg("Rest point reached. Stand up, stretch and drink some water."))]})

plugin("hourly-chime", "aincrad.hourly-chime", "Hourly Chime",
  "An SAO message on the hour, every hour.",
  {"scripts": [script(b("timer.every", {"seconds": 20}),
      b("control.if", {"condition": b("op.and", {"a": b("op.eq", {"a": now("minute"), "b": 0}),
                                                 "b": b("op.not", {"a": b("op.eq", {"a": now("hour"), "b": var("last")})})})}, body=[
          b("var.set", {"value": now("hour")}, {"name": "last"}),
          msg(join("It's ", now("time"), ". Keep climbing."))]))]})

# ---- Fun ---------------------------------------------------------------------------------

plugin("greeting", "aincrad.greeting", "Time Greeting",
  "Says good morning, afternoon or evening when AINCRAD starts.",
  {"scripts": [script(b("ext.started"),
      b("var.set", {"value": now("hour")}, {"name": "h"}),
      b("control.ifElse", {"condition": b("op.lt", {"a": var("h"), "b": 12})}, body=[msg("Good morning, player. Link start!")], else_=[
          b("control.ifElse", {"condition": b("op.lt", {"a": var("h"), "b": 18})},
            body=[msg("Good afternoon, player. Link start!")], else_=[msg("Good evening, player. Link start!")])]))]})

quotes = ["There's no such thing as a game you can't win.",
          "Even if I die, you keep living, okay?",
          "The only thing that matters is what you do with the time you have.",
          "A real fight is about how you live, not how you die.",
          "You can't give up. Not until the very end.",
          "Let's clear this floor together."]
def pick_quote():
    steps = [b("var.set", {"value": b("op.random", {"a": 1, "b": len(quotes)})}, {"name": "n"})]
    steps += [b("control.if", {"condition": b("op.eq", {"a": var("n"), "b": i + 1})}, body=[msg(q)]) for i, q in enumerate(quotes)]
    return steps
plugin("sao-quotes", "aincrad.sao-quotes", "Motivation",
  "A menu item that shows a random line of SAO-style encouragement.",
  {"menus": [{"id": "quotes", "name": "Motivation", "items": [noop("Inspire me", "sf:quote.bubble.fill")]}],
   "scripts": [script(chosen("Inspire me"), *pick_quote())]})

plugin("dice", "aincrad.dice", "Dice & Coins",
  "Roll a d6 or d20, or flip a coin, from the launcher.",
  {"menus": [{"id": "dice", "name": "Dice & Coins", "items": [
      noop("Roll a d6", "sf:dice.fill"), noop("Roll a d20", "sf:die.face.5.fill"), noop("Flip a coin", "sf:circle.circle.fill")]}],
   "scripts": [
      script(chosen("Roll a d6"), msg(join("You rolled ", b("op.random", {"a": 1, "b": 6}), "."))),
      script(chosen("Roll a d20"), msg(join("d20: ", b("op.random", {"a": 1, "b": 20}), "."))),
      script(chosen("Flip a coin"),
        b("control.ifElse", {"condition": b("op.eq", {"a": b("op.random", {"a": 1, "b": 2}), "b": 1})},
          body=[msg("Heads.")], else_=[msg("Tails.")]))]})

def game_scripts(app):
    return [script(b("app.launched", {"app": app}), b("looks.widgets", fields={"mode": "hide"}), msg(f"{app} started. Battle mode: widgets hidden.")),
            script(b("app.quit", {"app": app}), b("looks.widgets", fields={"mode": "show"}))]
plugin("battle-mode", "aincrad.battle-mode", "Battle Mode",
  "Hides your desktop widgets while Steam, Heroic or Prism Launcher is open, and brings them back when it quits.",
  {"scripts": game_scripts("Steam") + game_scripts("Heroic") + game_scripts("Prism Launcher")})

# ---- Themes ------------------------------------------------------------------------------

themes = {
  "black-swordsman": {"name": "Black Swordsman",
    "colors": {"panel": "#141518EE", "panelText": "#E6E8EC", "panelBorder": "#5A6070AA", "hover": "#24262CF5",
               "accent": "#7FA7FF", "iconBadge": "#E6E8EC", "iconGlyph": "#141518", "circle": "#1A1C20EE",
               "circleIcon": "#C9CED8", "circleBorder": "#7FA7FF88", "infoFooter": "#0E0F12F0", "infoIcon": "#7FA7FF"},
    "effects": {"tilt": 10, "shine": 0.12}},
  "flash": {"name": "The Flash",
    "colors": {"panel": "#FFFFFFF2", "panelText": "#3A2A2A", "panelBorder": "#C8303855", "hover": "#FFF1F1F8",
               "accent": "#D7263D", "iconBadge": "#3A2A2A", "iconGlyph": "#FFFFFF", "circle": "#FFFFFFF2",
               "circleIcon": "#6A5050", "circleBorder": "#D7263D88", "infoFooter": "#F6ECECF5", "infoIcon": "#D7263D"}},
  "sniper": {"name": "Sniper",
    "colors": {"panel": "#16201FEE", "panelText": "#D7EFEA", "panelBorder": "#3CC8B455", "hover": "#1F2E2CF5",
               "accent": "#3CC8B4", "iconBadge": "#D7EFEA", "iconGlyph": "#16201F", "circle": "#1A2624EE",
               "circleIcon": "#B9DAD4", "circleBorder": "#3CC8B488", "infoFooter": "#101817F0", "infoIcon": "#3CC8B4"},
    "geometry": {"cornerRadius": 2}, "effects": {"tilt": 8}},
  "navigation-pixie": {"name": "Navigation Pixie",
    "colors": {"panel": "#FFF7FBF2", "panelText": "#4A3A46", "panelBorder": "#F28CC055", "hover": "#FFEAF5F8",
               "accent": "#EE7DB8", "iconBadge": "#4A3A46", "iconGlyph": "#FFFFFF", "circle": "#FFF7FBF2",
               "circleIcon": "#7A6274", "circleBorder": "#EE7DB888", "infoFooter": "#FBEAF3F5", "infoIcon": "#EE7DB8"},
    "animation": {"preset": "gentle"}},
}
plugin("theme-pack", "aincrad.theme-pack", "Swordsman Theme Pack",
  "Four themes: Black Swordsman (dark, blue), The Flash (white, crimson), Sniper (teal) and Navigation Pixie (pink). Enable, then Install Themes.",
  {"themes": [f"themes/{k}.json" for k in themes]},
  files={f"themes/{k}.json": v for k, v in themes.items()})

# ---- Write -------------------------------------------------------------------------------

def write(root):
    for folder, (manifest, files) in plugins.items():
        d = os.path.join(root, folder)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        with open(os.path.join(d, "extension.json"), "w") as f:
            json.dump(manifest, f, indent=2, sort_keys=True, ensure_ascii=False)
        for rel, data in files.items():
            os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
            with open(os.path.join(d, rel), "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

write("src/extensions")
if len(sys.argv) > 2 and sys.argv[1] == "--app":
    write(os.path.join(sys.argv[2], "AINCRAD/Resources/Plugins"))
print(len(plugins), "plugins:", ", ".join(m["name"] for m, _ in plugins.values()))
