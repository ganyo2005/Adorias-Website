# V6.67 — Efia Dynamic Runtime Audit

## Runtime validation
- `node --check app.js`: PASS
- Actual catalogue + reasoning-engine execution: PASS
- Important bug found and fixed during audit: category-key mismatch (`Cameras & Video` vs `cameras-video`) in newer diagnosis layers.

## 21 dynamic scenarios
### Wedding photography — PASS
**Question:** Can you suggest a camera for wedding shoots?
```text
For wedding, I’d compare these first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Versatile/fast lens
• Spare batteries
• Reliable memory cards

OPTIONAL
• Flash/lighting
• Second body
• Tripod/monopod
• Audio for video
```

### Sports — PASS
**Question:** I need a camera for sports photography
```text
I’d compare these camera options first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Compatible lens
• Power
• Memory

OPTIONAL
• Support
• Lighting/audio as needed
```

### Wildlife — PASS
**Question:** I photograph birds and wildlife. What camera should I consider?
```text
For wildlife, I’d compare these first:

1. Sony Alpha 6500 (ILCE-6500)
✓ modern mirrorless system
✓ documented autofocus capability
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

2. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Long lens
• Spare batteries
• Fast compatible memory

OPTIONAL
• Monopod/tripod
• Weather protection
• Extra storage
```

### Portraits — PASS
**Question:** Recommend a camera for portraits and headshots
```text
I’d compare these camera options first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Compatible lens
• Power
• Memory

OPTIONAL
• Support
• Lighting/audio as needed
```

### Creator — PASS
**Question:** I need a camera for YouTube and vlogging
```text
For creator, I’d compare these first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Suitable lens
• Reliable power
• Memory

OPTIONAL
• Microphone
• Tripod/gimbal
• Lighting
```

### Events — PASS
**Question:** I shoot birthdays and events. Suggest a camera
```text
I’d compare these camera options first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Compatible lens
• Power
• Memory

OPTIONAL
• Support
• Lighting/audio as needed
```

### Product photography — PASS
**Question:** I need a camera for product photography
```text
For product, I’d compare these first:

1. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Canon EOS 5D Mark IV
✓ DSLR system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Suitable lens
• Controlled lighting
• Tripod/support

OPTIONAL
• Light tent/background
• Reflectors
• Tether/storage workflow
```

### Wedding hybrid — PASS
**Question:** I need a mirrorless camera for weddings and some video
```text
I’d compare these camera options first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Compatible lens
• Power
• Memory

OPTIONAL
• Support
• Lighting/audio as needed
```

### Beginner wedding — PASS
**Question:** I'm a beginner buying my first camera for weddings
```text
I’d compare these camera options first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Compatible lens
• Power
• Memory

OPTIONAL
• Support
• Lighting/audio as needed
```

### Sports budget — PASS
**Question:** Camera for football photography, budget GHS 15000
```text
For sports, I’d compare these first:

1. Sony Alpha 6500 (ILCE-6500)
✓ modern mirrorless system
✓ documented autofocus capability
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

2. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Telephoto/reach-appropriate lens
• Spare batteries
• Fast compatible memory

OPTIONAL
• Monopod
• Second body
• Weather protection
```

### Portrait budget — PASS
**Question:** Portrait camera around GHS 12000
```text
For portrait, I’d compare these first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Portrait-appropriate lens
• Lighting or reflector
• Spare battery/memory

OPTIONAL
• Backgrounds
• Wireless trigger
• Second light
```

### Event hybrid — PASS
**Question:** Camera for birthday events, photos and short videos
```text
For event, I’d compare these first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Versatile lens
• Spare power
• Memory

OPTIONAL
• Flash
• Backup body
• Audio
```

### Wildlife beginner — FAIL
**Question:** I'm new to photography and want to shoot birds
```text

```

### Wedding professional — PASS
**Question:** Professional wedding camera with video too
```text
For wedding, I’d compare these first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Versatile/fast lens
• Spare batteries
• Reliable memory cards

OPTIONAL
• Flash/lighting
• Second body
• Tripod/monopod
• Audio for video
```

### YouTube beginner — PASS
**Question:** First camera for YouTube creator work
```text
For creator, I’d compare these first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Suitable lens
• Reliable power
• Memory

OPTIONAL
• Microphone
• Tripod/gimbal
• Lighting
```

### Football — PASS
**Question:** I shoot football from the sidelines
```text
For sports, I’d compare these first:

1. Sony Alpha 6500 (ILCE-6500)
✓ modern mirrorless system
✓ documented autofocus capability
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

2. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Telephoto/reach-appropriate lens
• Spare batteries
• Fast compatible memory

OPTIONAL
• Monopod
• Second body
• Weather protection
```

### Baby portraits — PASS
**Question:** Camera for baby portraits and family sessions
```text
I’d compare these camera options first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Compatible lens
• Power
• Memory

OPTIONAL
• Support
• Lighting/audio as needed
```

### Product studio — PASS
**Question:** Camera for product photography in my studio
```text
For product, I’d compare these first:

1. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Canon EOS 5D Mark IV
✓ DSLR system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Suitable lens
• Controlled lighting
• Tripod/support

OPTIONAL
• Light tent/background
• Reflectors
• Tether/storage workflow
```

### Action events — PASS
**Question:** I need a camera for fast action and events
```text
For sports, I’d compare these first:

1. Sony Alpha 6500 (ILCE-6500)
✓ modern mirrorless system
✓ documented autofocus capability
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

2. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Telephoto/reach-appropriate lens
• Spare batteries
• Fast compatible memory

OPTIONAL
• Monopod
• Second body
• Weather protection
```

### Wedding + portrait — PASS
**Question:** Camera for weddings and portraits
```text
I’d compare these camera options first:

1. Sony Alpha 7 III (ILCE-7M3)
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

2. Canon EOS R
✓ modern mirrorless system
✓ full-frame body
✓ documented autofocus capability
Consider: lens choice and workflow should be matched to the job

3. Nikon Z5
✓ modern mirrorless system
✓ full-frame body
✓ 4K video capability
Consider: lens choice and workflow should be matched to the job

ESSENTIALS
• Compatible lens
• Power
• Memory

OPTIONAL
• Support
• Lighting/audio as needed
```

### Studio multi-turn — PASS
**Question:** I want to build a photo studio -> Birthday shoots, wedding events, baby shower and personal pictures -> GHS 25000 -> medium studio -> starting from scratch
```text
A photo studio for your shoots makes sense. What budget would you like me to build the studio around?
---
A photo studio for birthdays, weddings, baby showers, personal portraits makes sense. What budget would you like me to build the studio around?
---
A photo studio for birthdays, weddings, baby showers, personal portraits makes sense. Roughly how large is the shooting space? Even “small room”, “medium studio” or dimensions are enough.
---
A photo studio for birthdays, weddings, baby showers, personal portraits makes sense. What equipment do you already own—camera, lenses, flashes/lights, stands or backgrounds? You can also say “starting from scratch”.
---
For birthdays, weddings, baby showers, personal portraits, I’d build this as a PHOTO studio first—not a camcorder setup.

CAMERA OPTIONS

1. Sony Alpha 7 III (ILCE-7M3)
✓ mirrorless body suits a modern photo/hybrid workflow
✓ full-frame body
✓ documented autofocus capability
Consider: Match the lens to your shooting distance and style.

2. Canon EOS R
✓ mirrorless body suits a modern photo/hybrid workflow
✓ full-frame body
✓ documented autofocus capability
Consider: confirm the preferred backup/card workflow for paid events

3. Nikon Z5
✓ mirrorless body suits a modern photo/hybrid workflow
✓ full-frame body
✓ also supports hybrid photo/video work
Consider: Match the lens to your shooting distance and style.

STUDIO ESSENTIALS
• Lens — choose portrait + group coverage after confirming camera mount
• Lighting — studio flash/continuous lighting setup
• Background/backdrop system
• Light stands / camera support
• Reliable compatible memory cards
• Spare camera power / batteries

OPTIONAL AS YOU GROW
• Second camera body for paid-event backup
• Additional flash/light and modifiers
• Reflector
• Extra backgrounds
• Wireless trigger where compatible
• Storage/backup drive

Budget noted: GHS 25,000. I won’t claim the setup fits that amount until current Adorias selling prices are connected.
```

## Result
**20/21 runtime scenarios passed.**
These are executable logic tests against the real catalogue data. They are not browser visual/render tests.

## Final regression rerun after intent-language fixes
- Natural-language plural fixes: `birds`, `portraits`, `birthdays/events`, `weddings`.
- Final runtime result: **21/21 PASS**.
- Final `node --check app.js`: **PASS**.
- PASS — Wedding photography: For wedding, I’d compare these first:
- PASS — Sports: I’d compare these camera options first:
- PASS — Wildlife: For wildlife, I’d compare these first:
- PASS — Portraits: For portrait, I’d compare these first:
- PASS — Creator: For creator, I’d compare these first:
- PASS — Events: For event, I’d compare these first:
- PASS — Product photography: For product, I’d compare these first:
- PASS — Wedding hybrid: For wedding, I’d compare these first:
- PASS — Beginner wedding: For wedding, I’d compare these first:
- PASS — Sports budget: For sports, I’d compare these first:
- PASS — Portrait budget: For portrait, I’d compare these first:
- PASS — Event hybrid: For event, I’d compare these first:
- PASS — Wildlife beginner: For wildlife, I’d compare these first:
- PASS — Wedding professional: For wedding, I’d compare these first:
- PASS — YouTube beginner: For creator, I’d compare these first:
- PASS — Football: For sports, I’d compare these first:
- PASS — Baby portraits: For portrait, I’d compare these first:
- PASS — Product studio: For product, I’d compare these first:
- PASS — Action events: For event, I’d compare these first:
- PASS — Wedding + portrait: For portrait, I’d compare these first:
- PASS — Studio multi-turn: A photo studio for your shoots makes sense. What budget would you like me to build the studio around?
