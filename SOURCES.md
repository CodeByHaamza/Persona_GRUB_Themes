# 📎 Sources

Where every All-Out Attack illustration in this collection comes from.

The [Golden Rule](ROADMAP.md#-golden-rule-official-all-out-attacks-only) is that
a theme is only built on an **official All-Out Attack finisher image**. This file
is the proof of it: one line per theme, with the source its artwork came from.

> **The artwork is not ours.** The MIT licence covers the code in this repository
> and nothing else. Every illustration remains © ATLUS / © SEGA, and for Persona
> 5: The Phantom X also © Perfect World. Copyright lines printed on the artwork
> are never removed. This project is non-commercial.

---

## Persona 5: The Phantom X

### Added from the Megami Tensei Wiki

These ten themes were built from the official All-Out Attack "Finishing Touch"
illustrations hosted on the [Megami Tensei Wiki](https://megamitensei.fandom.com/),
at 1280×551 (Pinky at 2048×881, Wonder Velvet Room at 1280×720).

| Theme | Character | Source file |
|---|---|---|
| `blitz` | Kumi Katayama | [`Blitz AOA.png`](https://megamitensei.fandom.com/wiki/File:Blitz_AOA.png) |
| `miku` | Hatsune Miku | [`Miku AOA.png`](https://megamitensei.fandom.com/wiki/File:Miku_AOA.png) |
| `pinky` | Narumi Nashimoto | [`Narumi All out attack finisher.png`](https://megamitensei.fandom.com/wiki/File:Narumi_All_out_attack_finisher.png) |
| `joker_starlight` | Ren Amamiya | [`P5X Joker's Starlight Finishing Touch.png`](https://megamitensei.fandom.com/wiki/File:P5X_Joker%27s_Starlight_Finishing_Touch.png) |
| `mona_starlight` | Morgana | [`P5X Mona's Starlight Finishing Touch.png`](https://megamitensei.fandom.com/wiki/File:P5X_Mona%27s_Starlight_Finishing_Touch.png) |
| `panther_starlight` | Ann Takamaki | [`P5X Panther's Starlight Finishing Touch.png`](https://megamitensei.fandom.com/wiki/File:P5X_Panther%27s_Starlight_Finishing_Touch.png) |
| `wonder_velvet` | Nagisa Kamishiro | [`Wonder Velvet Room Finishing Touch.jpg`](https://megamitensei.fandom.com/wiki/File:Wonder_Velvet_Room_Finishing_Touch.jpg) |
| `wonder_shujin` | Nagisa Kamishiro | [`Wonder Shujin Finishing Touch.png`](https://megamitensei.fandom.com/wiki/File:Wonder_Shujin_Finishing_Touch.png) |
| `chord_summer` | Ayaka Sakai | [`Ayaka's Summer finishing touch.png`](https://megamitensei.fandom.com/wiki/File:Ayaka%E2%80%99s_Summer_finishing_touch.png) |
| `berry_summer` | Ichigo Shikano | [`Ichigo summer all out attack finisher.png`](https://megamitensei.fandom.com/wiki/File:Ichigo_summer_all_out_attack_finisher.png) |

The wiki files P5X artwork under the character's **real name**, not their
phantom-thief codename. The mapping used to find them comes from
[personadle](https://github.com/CodeByHaamza/personadle/blob/main/allOutAttackMode/database/personas_allOut.js).

### The 42 original themes

Captured from Persona 5: The Phantom X. All carry the
`©[2023] Perfect World` / `©SEGA ©ATLUS` line printed on the artwork, which is
kept intact. The Chinese promotional release was the only one available when
they were made; see [roadmap 1.3](ROADMAP.md#13-p5x-images-come-from-the-chinese-promo).

---

## Persona 3 Reload

| Theme | Source |
|---|---|
| `kotone` | [`P5X FeProtagonist AOA Battle gear full.png`](https://megamitensei.fandom.com/wiki/File:P5X_FeProtagonist_AOA_Battle_gear_full.png) — Kotone Shiomi's **official** All-Out Attack, as she appears in Persona 5: The Phantom X. This replaces a fan-made image that was used before. |

The other 12 are captured from Persona 3 Reload.

---

## Persona 5 Royal

The 13 themes are captured from Persona 5 Royal.

---

## Still to credit

The 67 themes that predate this file were made before sources were being
recorded. Their artwork is official in every case, but the exact page or capture
each one came from has not been written down yet. They should be filled in as
they are re-sourced — see
[roadmap 2.6](ROADMAP.md#26-sourcesmd).

## Known gaps

Two characters have an official All-Out Attack but no theme yet, because no
usable still of it has been found:

| Character | What exists | Why it is not enough |
|---|---|---|
| **Anri** (Aran Hirano) | `P5X Anri promo art.jpeg`, 3840×2160 | Promotional art, not an All-Out Attack. The Golden Rule forbids passing it off as one. |
| **Closer Radiance** (Motoha Arai, "Closer Sol") | `Motoha Sol all out attack render.png`, 1280×1113 | A cut-out character render with no background or text, so not the finisher composition. |

Both exist as animated captures in personadle, but only at 640×360 and 800×450
with a capture ID burnt into the frame, which is below the quality of every
theme here.

---

## Icons

The 102 distribution icons are not Persona artwork. Each is the distribution's
own logo, redrawn as a flat silhouette on a coloured square, and recoloured per
theme by [`tools/recolor_icons.py`](tools/recolor_icons.py). Every distribution
logo remains the property of its project.
