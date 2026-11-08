# Miami Cruise for Design tokens

The palette as JSON, for any app that isn't listed yet.

## Install

The theme files:

- [`tokens.json`](tokens.json): Palette tokens
- [`contrast.json`](contrast.json): Contrast ratios

Run the commands below from this folder, or from wherever you saved the file.

### 1. Read the tokens

The file has a `dark` and a `light` object, each mapping a token name to a hex colour. `contrast.json` lists the contrast ratios if you want to check your own pairings.

```python
import json

tokens = json.load(open("tokens.json"))
print(tokens["dark"]["accent"])  # the hero colour
```

### 2. Map them to your app

`accent` is the single highlight colour: primary action, selection, focus, links. `success`, `warning`, `danger` and `info` are green, yellow, red and cyan. `text`, `muted` and `disabled` are the text ramp. `bg`, `panel`, `border`, `hover` and `row` are surfaces. `on-accent` is the text colour to use on an `accent` fill. The full role table is in the porting guide.

> [!NOTE]
> Every text and accent colour is at least 4.5:1 against `bg`, so you can use them for text without checking.

## Details

- **Variants:** dark and light
- **Covers:** 17 tokens in dark and light, plus contrast ratios against the background
- **Glow:** n/a
- **Tested:** Generated from the same source as every other target

## More

- [Website page for Design tokens](https://lanjelin.github.io/miami-cruise/apps/tokens.html)
- [Palette and specification](../../docs/SPEC.md)
- [Report a problem](https://github.com/lanjelin/miami-cruise/issues/new/choose)
- [MIT licence](../../LICENSE)
