# MakeyBot Robot Registry — Reference Guide

This document is the human-readable companion to `robot_registry.jsonl`.

- **`robot_registry.jsonl`** — machine-readable specification. The Raspberry Pi loads this at boot to know what features it supports, what values are valid, and what default state to start in.
- **`robot_commands.jsonl`** — live activity log. Commands from students and responses from the robot are appended here as single-line JSON (JSONL).
- **`robot_registry.md`** (this file) — human-readable reference. Use this to understand every option and write correct commands.

---

## How Commands Work

A **controller** (student laptop, web form, another robot) writes a `command` entry to `robot_commands.jsonl`.
The **robot** (Raspberry Pi) polls the file, reads the command, validates it against the registry, and either:
- Writes a `command_acknowledged` entry and executes, or
- Writes a `command_rejected` entry with a reason.

After execution the robot writes a `current_state` entry showing its full state.

**Commands only need to include the features being changed.** Omitted features are left in their current state.

---

## Message Types

All entries share three required fields: `robot`, `timestamp`, and `message_type`.

| message_type | Sent by | Purpose |
|---|---|---|
| `login` | Robot | Robot came online |
| `logout` | Robot | Robot going offline |
| `heartbeat` | Robot | Periodic keep-alive |
| `command` | Controller | Request to change robot state |
| `command_acknowledged` | Robot | Command accepted, executing |
| `command_rejected` | Robot | Command refused, with reason |
| `current_state` | Robot | Full snapshot of all features |
| `processed_offline_commands` | Robot | Commands executed while offline |
| `ignored_offline_commands` | Robot | Commands discarded (e.g. stale) |

### login / logout
```json
{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:00:00",
 "message_type": "login", "sent_by": "student_alice",
 "message": "RobotAlpha is online and ready."}
```

### heartbeat
```json
{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:05:00",
 "message_type": "heartbeat", "sent_by": "student_alice"}
```

### command
```json
{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:07:30",
 "message_type": "command", "sent_by": "student_bob",
 "request_id": "RobotAlpha_bob_0001",
 "features": { ... }}
```
`request_id` format: `RobotName_sender_sequence` — e.g. `RobotAlpha_bob_0001`

### command_acknowledged / command_rejected
```json
{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:07:32",
 "message_type": "command_acknowledged", "sent_by": "student_alice",
 "request_id": "RobotAlpha_bob_0001", "message": "Command received. Executing now."}

{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:10:02",
 "message_type": "command_rejected", "sent_by": "student_alice",
 "request_id": "RobotAlpha_carol_0001",
 "message": "Rejected: set_eye_strobe duration 999999 exceeds maximum of 10000ms."}
```

### current_state
Full snapshot — includes all features regardless of what changed.
```json
{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:07:33",
 "message_type": "current_state", "sent_by": "student_alice",
 "features": {"eyes": { ... }, "stop_light": { ... }, "servo": {}}}
```

### processed_offline_commands / ignored_offline_commands
```json
{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:25:01",
 "message_type": "processed_offline_commands", "sent_by": "student_alice",
 "commands_processed": ["RobotAlpha_bob_0003", "RobotAlpha_carol_0002"]}

{"robot": "RobotAlpha", "timestamp": "2026-02-28T09:30:01",
 "message_type": "ignored_offline_commands", "sent_by": "student_alice",
 "commands_ignored": ["RobotAlpha_bob_0004", "RobotAlpha_carol_0003"]}
```

---

## Features

The `features` object in a `command` or `current_state` entry contains one or more of:

```
features
├── eyes
├── stop_light
└── servo
```

---

## Feature: eyes

Controls the two RGB LED eyes. Each eye has an independent color. Most animation effects apply to **both eyes simultaneously**.

### Eye color

Set each eye independently using `[R, G, B]` values from 0–255.

```json
{"features": {"eyes": {
  "set_right_rgb_eye_color": [255, 100, 0],
  "set_left_rgb_eye_color":  [0, 200, 255]
}}}
```

Lock the left eye to always mirror the right eye:
```json
{"features": {"eyes": {
  "set_lock_left_to_right_eye": true,
  "set_right_rgb_eye_color": [255, 0, 0]
}}}
```

### set_eye_emotion_preset

High-level shortcut that maps to a combination of lower-level eye settings.

| Option | Description |
|---|---|
| `neutral` | Default — eyes off or dim white |
| `happy` | Bright warm color, gentle pulse |
| `angry` | Red, rapid strobe |
| `sleepy` | Dim, slow blink |
| `confused` | Random color changes |
| `excited` | Fast color cycle |

```json
{"features": {"eyes": {"set_eye_emotion_preset": "happy"}}}
```

### set_right_eye_blink / set_left_eye_blink

Slow deliberate on/off blink on one eye. Can be randomised.

| Key | Type | Range | Default | Description |
|---|---|---|---|---|
| `active` | boolean | — | false | Enable/disable |
| `interval` | integer ms | 500–10000 | 1000 | Time between blinks |
| `duration` | integer ms | 50–500 | 200 | How long the eye is off during a blink |
| `random` | boolean | — | false | If true, interval is randomised |
| `random_min_interval` | integer ms | 10000–60000 | 10000 | Minimum random interval |
| `random_max_interval` | integer ms | 10000–60000 | 30000 | Maximum random interval |

```json
{"features": {"eyes": {
  "set_right_eye_blink": {"active": true, "interval": 3000, "duration": 150, "random": false}
}}}
```

Random blink (natural feel):
```json
{"features": {"eyes": {
  "set_left_eye_blink": {
    "active": true, "random": true,
    "random_min_interval": 5000, "random_max_interval": 20000, "duration": 150
  }
}}}
```

### set_eye_strobe

Rapid continuous flicker on both eyes.

| Key | Type | Range | Default | Description |
|---|---|---|---|---|
| `active` | boolean | — | false | Enable/disable |
| `speed` | integer ms | 50–500 | 100 | Interval between flashes |
| `duration` | integer ms | 500–10000 | 1000 | How long the strobe runs |

```json
{"features": {"eyes": {
  "set_eye_strobe": {"active": true, "speed": 80, "duration": 3000}
}}}
```

### set_eye_pulse

Rhythmic heartbeat-style brightness fade on both eyes. Requires PWMLED.

| Key | Type | Range | Default | Description |
|---|---|---|---|---|
| `active` | boolean | — | false | Enable/disable |
| `rate` | integer ms | 200–5000 | 1000 | One full pulse cycle |
| `min_brightness` | integer % | 0–100 | 0 | Dimmest point |
| `max_brightness` | integer % | 0–100 | 100 | Brightest point |

```json
{"features": {"eyes": {
  "set_eye_pulse": {"active": true, "rate": 1200, "min_brightness": 10, "max_brightness": 100}
}}}
```

### set_eye_color_shift

One-time smooth transition between two colors on both eyes.

| Key | Type | Default | Description |
|---|---|---|---|
| `active` | boolean | false | Enable/disable |
| `color_from` | `[R,G,B]` or `"random"` | `[0,0,0]` | Starting color |
| `color_to` | `[R,G,B]` or `"random"` | `[255,255,255]` | Ending color |
| `duration` | integer ms 500–10000 | 2000 | Transition time |

```json
{"features": {"eyes": {
  "set_eye_color_shift": {
    "active": true,
    "color_from": [255, 0, 0],
    "color_to": [0, 0, 255],
    "duration": 3000
  }
}}}
```

### set_eye_color_cycle

Continuously loops through a list of 2–10 colors on both eyes.

| Key | Type | Default | Description |
|---|---|---|---|
| `active` | boolean | false | Enable/disable |
| `colors` | list of `[R,G,B]` | red/green/blue | 2–10 colors to cycle through |
| `speed` | integer ms 100–5000 | 1000 | Time per color step |
| `loop` | boolean | true | Repeat or run once |

```json
{"features": {"eyes": {
  "set_eye_color_cycle": {
    "active": true,
    "colors": [[255,0,0],[255,165,0],[255,255,0],[0,255,0],[0,0,255]],
    "speed": 800,
    "loop": true
  }
}}}
```

### set_eye_random_color

Randomly changes both eye colors at a set interval.

| Key | Type | Range | Default |
|---|---|---|---|
| `active` | boolean | — | false |
| `interval` | integer ms | 500–30000 | 5000 |

```json
{"features": {"eyes": {
  "set_eye_random_color": {"active": true, "interval": 2000}
}}}
```

---

## Feature: stop_light

Controls the three-LED stop light (Red / Yellow / Green). Has three top-level modes: `traffic`, `freeform`, and `off`.

### mode: off

All LEDs off. No additional settings required.

```json
{"features": {"stop_light": {"mode": "off"}}}
```

---

### mode: traffic

Rule-based signal behavior. `sub_mode` is required.

| sub_mode | Behavior |
|---|---|
| `stop` | Blinking red only (500ms interval, 250ms on) |
| `caution` | Blinking yellow only (750ms interval, 375ms on) |
| `go` | Solid green only |
| `cycle` | Auto-sequences red → yellow → green → yellow → red |

```json
{"features": {"stop_light": {"mode": "traffic", "sub_mode": "go"}}}
```

```json
{"features": {"stop_light": {"mode": "traffic", "sub_mode": "caution"}}}
```

For `cycle`, you can optionally set durations:
```json
{"features": {"stop_light": {
  "mode": "traffic",
  "sub_mode": "cycle",
  "cycle_settings": {
    "red_duration": 5000,
    "yellow_duration": 2000,
    "green_duration": 5000
  }
}}}
```

| Key | Range | Default |
|---|---|---|
| `red_duration` | 1000–30000 ms | 5000 |
| `yellow_duration` | 500–10000 ms | 2000 |
| `green_duration` | 1000–30000 ms | 5000 |

---

### mode: freeform

Direct independent control of each LED. Each LED has its own `mode` key that is the single source of truth for its behavior. Only one behavior can be active per LED at a time.

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    { ... },
  "yellow_led": { ... },
  "green_led":  { ... }
}}}
```

Available LED modes: `on`, `off`, `blink`, `strobe`, `fade`, `pulse`, `dim`, `morse_message`

---

#### LED mode: on / off

No settings required.

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "on"},
  "yellow_led": {"mode": "off"},
  "green_led":  {"mode": "on"}
}}}
```

---

#### LED mode: blink

Slow deliberate on/off blink.

| Key | Type | Range | Description |
|---|---|---|---|
| `interval` | integer ms | 100–10000 | Time between blinks |
| `duration` | integer ms | 50–5000 | How long the LED is on per blink |
| `random` | boolean | — | Randomise interval |
| `random_min_interval` | integer ms | 10000–60000 | Min random interval |
| `random_max_interval` | integer ms | 10000–60000 | Max random interval |

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "blink", "blink": {"interval": 500, "duration": 250, "random": false}},
  "yellow_led": {"mode": "off"},
  "green_led":  {"mode": "on"}
}}}
```

---

#### LED mode: strobe

Rapid continuous flicker.

| Key | Type | Range | Description |
|---|---|---|---|
| `speed` | integer ms | 50–500 | Flash interval |
| `duration` | integer ms | 500–10000 | How long the strobe runs |

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "strobe", "strobe": {"speed": 80, "duration": 5000}},
  "yellow_led": {"mode": "off"},
  "green_led":  {"mode": "off"}
}}}
```

---

#### LED mode: fade

Ramps LED brightness using PWM. `up` and `down` control direction.
If both are `true`, the LED fades up then down in a continuous cycle.
Requires PWMLED.

| Key | Type | Default | Description |
|---|---|---|---|
| `up` | boolean | true | Ramp from off to full brightness |
| `down` | boolean | false | Ramp from full brightness to off |
| `duration` | integer ms 100–10000 | 1000 | Time per direction. Full up+down cycle = 2× this value |
| `loop` | boolean | true | Repeat continuously or run once |

Fade up only:
```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "off"},
  "yellow_led": {"mode": "fade", "fade": {"up": true, "down": false, "duration": 1500, "loop": true}},
  "green_led":  {"mode": "off"}
}}}
```

Fade up then down (full cycle):
```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "off"},
  "yellow_led": {"mode": "off"},
  "green_led":  {"mode": "fade", "fade": {"up": true, "down": true, "duration": 2000, "loop": true}}
}}}
```

---

#### LED mode: pulse

Rhythmic brightness animation using PWM. `pattern` selects the waveform shape. `rate` scales the overall speed. Requires PWMLED.

| Key | Type | Range | Default | Description |
|---|---|---|---|---|
| `pattern` | string | see below | `sine` | Waveform shape |
| `rate` | integer ms | 200–10000 | 1000 | One full cycle duration |
| `min_brightness` | integer % | 0–100 | 0 | Dimmest point |
| `max_brightness` | integer % | 0–100 | 100 | Brightest point |
| `loop` | boolean | — | true | Repeat or run once |

**Patterns:**

| Pattern | Description |
|---|---|
| `sine` | Default. Smooth continuous rise-and-fall sine wave. |
| `heart` | Double-beat lub-dub: quick rise, partial fall, rise again, then a long rest. |
| `breathe` | Very slow inhale-hold-exhale-hold cycle. Calm and meditative. |
| `flutter` | Fast organic flicker with irregular cadence. Candle or flame feel. |
| `alert` | Sharp single flash followed by a long dark pause. Alarm or warning. |
| `bounce` | Ramps up quickly then decays in diminishing steps, like a dropped ball. |

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "pulse", "pulse": {"pattern": "heart", "rate": 800, "min_brightness": 0, "max_brightness": 100, "loop": true}},
  "yellow_led": {"mode": "off"},
  "green_led":  {"mode": "off"}
}}}
```

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "off"},
  "yellow_led": {"mode": "pulse", "pulse": {"pattern": "flutter", "rate": 300, "min_brightness": 20, "max_brightness": 100, "loop": true}},
  "green_led":  {"mode": "pulse", "pulse": {"pattern": "breathe", "rate": 4000, "min_brightness": 0, "max_brightness": 100, "loop": true}}
}}}
```

---

#### LED mode: dim

Holds the LED at a fixed PWM brightness. Requires PWMLED.

| Key | Type | Range | Default | Description |
|---|---|---|---|---|
| `brightness` | integer % | 1–99 | 50 | Fixed level. Use `on` for 100%, `off` for 0%. |

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "dim", "dim": {"brightness": 30}},
  "yellow_led": {"mode": "dim", "dim": {"brightness": 75}},
  "green_led":  {"mode": "on"}
}}}
```

---

#### LED mode: morse_message

Flashes any text as Morse code. Dot and dash timing is calculated automatically from `wpm` using the standard PARIS method. Unsupported characters are skipped.

| Key | Type | Range | Default | Description |
|---|---|---|---|---|
| `message` | string | — | `"SOS"` | Text to transmit in Morse code |
| `wpm` | integer | 1–30 | 5 | Speed in words per minute. 1 wpm = 240ms dot. |
| `loop` | boolean | — | true | Repeat continuously or transmit once |

**PARIS timing reference:**

| wpm | dot (ms) | dash (ms) |
|---|---|---|
| 5 | 240 | 720 |
| 10 | 120 | 360 |
| 15 | 80 | 240 |
| 20 | 60 | 180 |

```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "off"},
  "yellow_led": {"mode": "off"},
  "green_led":  {"mode": "morse_message", "morse_message": {"message": "HELLO", "wpm": 8, "loop": true}}
}}}
```

SOS once only (no loop):
```json
{"features": {"stop_light": {
  "mode": "freeform",
  "red_led":    {"mode": "morse_message", "morse_message": {"message": "SOS", "wpm": 5, "loop": false}},
  "yellow_led": {"mode": "off"},
  "green_led":  {"mode": "off"}
}}}
```

---

## Feature: servo

Servo control is not yet designed. This feature is reserved for a future lab.

```json
{"features": {"servo": {}}}
```

---

## Quick Reference — freeform LED modes

| Mode | PWM needed | Key params |
|---|---|---|
| `on` | No | none |
| `off` | No | none |
| `blink` | No | `interval`, `duration`, `random` |
| `strobe` | No | `speed`, `duration` |
| `fade` | Yes | `up`, `down`, `duration`, `loop` |
| `pulse` | Yes | `pattern`, `rate`, `min_brightness`, `max_brightness`, `loop` |
| `dim` | Yes | `brightness` (1–99%) |
| `morse_message` | No | `message`, `wpm`, `loop` |
