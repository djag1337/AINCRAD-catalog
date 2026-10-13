"""Writes the example extensions in src/extensions. They're ordinary extension.json files:
open any of them in AINCRAD's Extension Studio to see or change the blocks."""
import json, os

def lit(v): return {"op": "literal", "fields": {"value": str(v)}}
def b(op, inputs=None, fields=None, body=None, else_=None):
    x = {"op": op, "inputs": {k: (v if isinstance(v, dict) else lit(v)) for k, v in (inputs or {}).items()},
         "fields": fields or {}}
    if body is not None: x["body"] = body
    if else_ is not None: x["elseBody"] = else_
    return x
def var(name): return b("var.get", fields={"name": name})
def script(trigger, *steps): return {"trigger": trigger, "steps": list(steps)}
def gauge(ext, name, label, show="bar"):
    return {"name": label, "widget": {"type": "stat", "width": 260, "height": 70,
            "props": {"source": f"script:{ext}/{name}", "show": show, "label": name}}}

def write(folder, manifest):
    os.makedirs(f"src/extensions/{folder}", exist_ok=True)
    with open(f"src/extensions/{folder}/extension.json", "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

base = {"version": "1.0", "apiVersion": 1, "author": "AINCRAD"}

write("system-hp", {**base, "id": "aincrad.system-hp", "name": "System HP",
  "description": "Your Mac's free CPU as an SAO HP gauge, updated every 5 seconds. Add the “HP gauge” widget from the Widgets library.",
  "permissions": [], "provides": {
    "scripts": [script(b("timer.every", {"seconds": 5}),
        b("var.set", {"value": b("op.sub", {"a": 100, "b": b("sense.reading", fields={"reading": "CPU"})})}, {"name": "hp"}),
        b("looks.gauge", {"name": "HP", "text": b("op.join", {"a": var("hp"), "b": " / 100"}), "percent": var("hp")}))],
    "widgets": [gauge("aincrad.system-hp", "HP", "HP gauge")]}})

write("steam-mode", {**base, "id": "aincrad.steam-mode", "name": "Steam Mode",
  "description": "Switches to the Gun Gale theme while Steam is open, and back to Aincrad Classic when it quits. Install the Gun Gale theme first.",
  "permissions": [], "provides": {"scripts": [
    script(b("app.launched", {"app": "Steam"}),
        b("looks.theme", {"theme": "gun-gale"}),
        b("looks.message", {"text": "Link start! Gun Gale mode on."})),
    script(b("app.quit", {"app": "Steam"}),
        b("looks.theme", {"theme": "aincrad-classic"}),
        b("looks.message", {"text": "Back to Aincrad."}))]}})

write("focus-timer", {**base, "id": "aincrad.focus-timer", "name": "Focus Timer",
  "description": "A 25-minute focus timer. Add its “Focus” menu to your launcher as a Dynamic list, and the Focus gauge widget to your desktop.",
  "permissions": [], "provides": {
    "menus": [{"id": "focus", "name": "Focus", "items": [
        {"name": "Start 25-minute focus", "icon": "sf:timer", "action": {"type": "builtin", "target": "none"}},
        {"name": "Stop focus", "icon": "sf:stop.circle.fill", "action": {"type": "builtin", "target": "none"}}]}],
    "scripts": [
      script(b("item.chosen", {"name": "Start 25-minute focus"}),
        b("var.set", {"value": 25}, {"name": "minutes"}),
        b("var.set", {"value": 1}, {"name": "active"}),
        b("looks.gauge", {"name": "Focus", "text": "25 min left", "percent": 100}),
        b("looks.message", {"text": "Focus started: 25 minutes."})),
      script(b("item.chosen", {"name": "Stop focus"}),
        b("var.set", {"value": 0}, {"name": "active"}),
        b("looks.gauge", {"name": "Focus", "text": "stopped", "percent": 0})),
      script(b("timer.every", {"seconds": 60}),
        b("control.if", {"condition": b("op.eq", {"a": var("active"), "b": 1})}, body=[
          b("var.change", {"value": -1}, {"name": "minutes"}),
          b("looks.gauge", {"name": "Focus", "text": b("op.join", {"a": var("minutes"), "b": " min left"}),
                            "percent": b("op.mul", {"a": var("minutes"), "b": 4})}),
          b("control.if", {"condition": b("op.lt", {"a": var("minutes"), "b": 1})}, body=[
            b("var.set", {"value": 0}, {"name": "active"}),
            b("looks.message", {"text": "Focus session complete! Take a break."}),
            b("looks.gauge", {"name": "Focus", "text": "done", "percent": 0})])]))],
    "widgets": [gauge("aincrad.focus-timer", "Focus", "Focus gauge")]}})

write("welcome", {**base, "id": "aincrad.welcome", "name": "Welcome Message",
  "description": "Greets you with the classic SAO message when AINCRAD starts, and counts how often you open the launcher.",
  "permissions": [], "provides": {"scripts": [
    script(b("ext.started"), b("looks.message", {"text": "Welcome to Sword Art Online!"})),
    script(b("launcher.opened"),
        b("var.change", {"value": 1}, {"name": "opens"}),
        b("looks.gauge", {"name": "Opens", "text": b("op.join", {"a": var("opens"), "b": " opens today"}), "percent": ""}))],
    "widgets": [gauge("aincrad.welcome", "Opens", "Launcher counter", show="text")]}})

weather_steps = [
    b("var.set", {"value": b("sense.fetch", {"url": "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01&current=temperature_2m"})}, {"name": "json"}),
    b("var.set", {"value": b("sense.json", {"path": "current.temperature_2m", "json": var("json")})}, {"name": "temp"}),
    b("looks.gauge", {"name": "Weather", "text": b("op.join", {"a": var("temp"), "b": "°C"}),
                      "percent": b("op.mul", {"a": b("op.add", {"a": var("temp"), "b": 10}), "b": 2.5})})]
write("weather", {**base, "id": "aincrad.weather", "name": "Weather",
  "description": "Current temperature from Open-Meteo (no account needed), every 15 minutes. Open it in the Studio to change the latitude and longitude in the fetch block.",
  "permissions": ["network"], "provides": {
    "scripts": [script(b("ext.started"), *weather_steps), script(b("timer.every", {"seconds": 900}), *weather_steps)],
    "widgets": [gauge("aincrad.weather", "Weather", "Weather gauge")]}})
print("wrote", sorted(os.listdir("src/extensions")))
