"""Fixed wallpaper assets; builds copy approved PNGs, never regenerate imagery."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export(pals, dist):
    out = dist/'wallpapers'
    out.mkdir(parents=True, exist_ok=True)
    for variant in ('dark', 'light'):
        name = f'miami-coast-{variant}-4k.png'
        shutil.copyfile(ROOT/'wallpapers'/name, out/name)
    shutil.copyfile(ROOT/'LICENSE', out/'LICENSE.txt')


GUIDE = dict(
    name='Wallpapers', category='Desktop', mono='WP', tags=['4K','Wallpaper'],
    aliases='wallpaper background miami coast desktop skyline sunset',
    status='Dark and light 4K companions; user visually approved',
    tagline='A quiet coast, a magenta sun and room to breathe. Miami Coast in dark and light.',
    files=[(f'wallpapers/miami-coast-{v}-4k.png',f'miami-coast-{v}-4k.png',f'{v.title()} wallpaper · 3840 × 2160 PNG') for v in ('dark','light')]+[('wallpapers/LICENSE.txt','LICENSE.txt','MIT licence')],
    shots=[(f'wallpapers/{v}.png',f'Miami Coast wallpaper · {v} · preview of the 4K download') for v in ('dark','light')],
    file_note='Choose either wallpaper or keep both. These are optional companions to the desktop theme and icons; nothing is applied automatically. AI-generated artwork, enhanced with super-resolution and exported at 3840 × 2160.',
    tested='Both final PNGs visually reviewed, dimensions and file integrity checked. Super-resolution tile-boundary checks passed; originals and desktop settings preserved',
    covers='A matching dark/light coastal skyline with quiet space on the left for desktop icons. Designed for 16:9 displays',
    glow='Soft cyan horizon and restrained magenta sunset; baked into the image',
    steps=[('Save your wallpaper',[
        ('p','Save the Dark or Light PNG somewhere you want to keep it, such as your Pictures/Wallpapers folder. Keep the file there while it is selected as your background.'),
        ('note','Each download is a 3840 × 2160 image. Other aspect ratios may crop the scene depending on your desktop’s scaling setting.'),
    ]),('Set your background',[
        ('p','In XFCE, right-click the desktop and open Desktop Settings → Background. Note your current image and scaling setting, then choose the folder containing Miami Coast and select the image. Zoomed fills the screen; Scaled keeps the whole image visible.'),
        ('note','Choose the intended display and workspace before applying. Leave any options to apply across all workspaces or displays unchanged unless that is what you want. Other desktops provide similar controls in their background settings.'),
    ]),('Restore your previous background',[
        ('p','Open the same background settings and select your previous image and scaling setting. Restore only the displays and workspaces you changed. Switch away from Miami Coast before removing its PNG.'),
        ('note','The wallpapers are offered under the collection’s MIT licence. They are AI-generated and super-resolution upscaled, not native-resolution photographs or pixel-exact palette exports.'),
    ])],
)
