#!/usr/bin/python3
"""Native GTK3 control-state/contrast audit in the private desktop session."""
from pathlib import Path
import json
import sys
import gi
gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0')
from gi.repository import Gtk,Gdk,GLib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from palette import build_palette,contrast

mode=sys.argv[1]
report=Path(sys.argv[2])
p=build_palette(mode)[0]
window=Gtk.Window(title='Controls — Miami Cruise '+mode.title())
window.set_default_size(980,650);window.move(350,110)
box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=14)
box.set_border_width(20);window.add(box)
menu=Gtk.MenuBar()
file=Gtk.MenuItem(label='File');menu.append(file)
popup=Gtk.Menu();file.set_submenu(popup)
for name in ('New project','Open…','Save','Unavailable'):
    item=Gtk.MenuItem(label=name)
    if name=='Unavailable':item.set_sensitive(False)
    popup.append(item)
box.pack_start(menu,False,False,0)
notebook=Gtk.Notebook();box.pack_start(notebook,True,True,0)
grid=Gtk.Grid(column_spacing=20,row_spacing=14)
grid.set_border_width(20)
notebook.append_page(grid,Gtk.Label(label='Controls'))
text=Gtk.TextView();text.get_buffer().set_text('Miami Cruise\nSynthetic text editor sample.\nSelected text should remain readable.')
notebook.append_page(text,Gtk.Label(label='Text editor'))
buttons=[]
other_labels=[]
for index,(name,style) in enumerate([('Default',None),('Suggested','suggested-action'),('Destructive','destructive-action'),('Flat','flat')]):
    b=Gtk.Button(label=name)
    if style:b.get_style_context().add_class(style)
    grid.attach(b,index,0,1,1);buttons.append((name,b))
entry=Gtk.Entry();entry.set_text('Editable text');grid.attach(entry,0,1,2,1)
disabled=Gtk.Entry();disabled.set_text('Disabled entry');disabled.set_sensitive(False);grid.attach(disabled,2,1,2,1)
for i,on in enumerate((True,False)):
    check=Gtk.CheckButton(label='Checked' if on else 'Unchecked');check.set_active(on);grid.attach(check,i,2,1,1)
radio=Gtk.RadioButton.new_with_label(None,'Radio');grid.attach(radio,2,2,1,1)
switch=Gtk.Switch();switch.set_active(True);grid.attach(switch,3,2,1,1)
combo=Gtk.ComboBoxText();combo.append_text('Dark / Light');combo.append_text('Follow system');combo.set_active(0);grid.attach(combo,0,3,2,1)
spin=Gtk.SpinButton.new_with_range(0,100,1);spin.set_value(42);grid.attach(spin,2,3,2,1)
scale=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,100,1);scale.set_value(65);grid.attach(scale,0,4,4,1)
label=Gtk.Label(label='Disabled label');label.set_sensitive(False);grid.attach(label,0,5,2,1);other_labels.append(('Disabled label',label,True))
link=Gtk.LinkButton.new_with_label('https://example.invalid/','Example link');grid.attach(link,2,5,2,1)
store=Gtk.ListStore(str,str)
for row in [('Notes.txt','Text'),('Projects','Folder'),('palette.json','JSON')]:store.append(row)
view=Gtk.TreeView(model=store)
for i,name in enumerate(('Name','Type')):view.append_column(Gtk.TreeViewColumn(name,Gtk.CellRendererText(),text=i))
view.get_selection().select_path(Gtk.TreePath.new_from_string('1'))
grid.attach(view,0,6,4,1)
progress=Gtk.ProgressBar();progress.set_fraction(.65);grid.attach(progress,0,7,4,1)
window.show_all();window.present()
Gtk.Settings.get_default().set_property('gtk-enable-animations',False)
results=[]
def hx(c):return '#%02x%02x%02x'%tuple(round(v*255) for v in (c.red,c.green,c.blue))
def audit():
    states=[Gtk.StateFlags.NORMAL,Gtk.StateFlags.FOCUSED,
            Gtk.StateFlags.FOCUSED|Gtk.StateFlags.PRELIGHT,
            Gtk.StateFlags.PRELIGHT,Gtk.StateFlags.ACTIVE,
            Gtk.StateFlags.CHECKED,Gtk.StateFlags.BACKDROP,
            Gtk.StateFlags.PRELIGHT|Gtk.StateFlags.BACKDROP,
            Gtk.StateFlags.ACTIVE|Gtk.StateFlags.BACKDROP,
            Gtk.StateFlags.CHECKED|Gtk.StateFlags.BACKDROP,
            Gtk.StateFlags.INSENSITIVE,Gtk.StateFlags.INSENSITIVE|Gtk.StateFlags.BACKDROP]
    for name,button in buttons:
        original=button.get_state_flags()
        for state in states:
            button.set_state_flags(state,True)
            while Gtk.events_pending():Gtk.main_iteration_do(False)
            context=button.get_style_context()
            bg=context.get_background_color(context.get_state())
            if bg.alpha<.99:
                bghex=p['bg']
            else:bghex=hx(bg)
            label=button.get_child()
            ctx=label.get_style_context()
            fg=hx(ctx.get_color(ctx.get_state()))
            ratio=contrast(fg,bghex)
            minimum=3 if state & Gtk.StateFlags.INSENSITIVE else 4.5
            results.append({'control':name,'state':int(state),'foreground':fg,'background':bghex,'contrast':round(ratio,2),'passed':ratio>=minimum})
        button.set_state_flags(original,True)
    # Also audit inherited text in unfocused/disabled views, not only buttons.
    for widget_name,target,is_disabled in other_labels + [('Entry',entry,False),('Disabled entry',disabled,True),('Tab',notebook.get_tab_label(text),False)]:
        original=target.get_state_flags()
        for backdrop in (Gtk.StateFlags.NORMAL,Gtk.StateFlags.BACKDROP):
            state=backdrop | (Gtk.StateFlags.INSENSITIVE if is_disabled else Gtk.StateFlags.NORMAL)
            target.set_state_flags(state,True)
            while Gtk.events_pending():Gtk.main_iteration_do(False)
            context=target.get_style_context()
            fg=hx(context.get_color(context.get_state()))
            parent=target
            bg=None
            while parent is not None:
                ctx=parent.get_style_context(); candidate=ctx.get_background_color(ctx.get_state())
                if candidate.alpha>.99:
                    bg=hx(candidate);break
                parent=parent.get_parent()
            bg=bg or p['bg']
            ratio=contrast(fg,bg)
            results.append({'control':widget_name,'state':int(state),'foreground':fg,'background':bg,'contrast':round(ratio,2),'passed':ratio >= (3 if is_disabled else 4.5)})
        target.set_state_flags(original,True)
    # Audit menu labels themselves: container-only checks miss inherited panel
    # and active-button foregrounds. Include popup and menubar, focused/backdrop.
    for container in (menu, popup):
        for item in container.get_children():
            label=item.get_child()
            original=item.get_state_flags()
            for state in (Gtk.StateFlags.NORMAL, Gtk.StateFlags.PRELIGHT,
                          Gtk.StateFlags.BACKDROP,
                          Gtk.StateFlags.PRELIGHT|Gtk.StateFlags.BACKDROP,
                          Gtk.StateFlags.INSENSITIVE):
                item.set_state_flags(state,True)
                while Gtk.events_pending():Gtk.main_iteration_do(False)
                ctx=item.get_style_context()
                bg=hx(ctx.get_background_color(ctx.get_state()))
                ctx=label.get_style_context()
                fg=hx(ctx.get_color(ctx.get_state()))
                ratio=contrast(fg,bg)
                results.append({'control':'Menu '+label.get_text(),'state':int(state),
                                'foreground':fg,'background':bg,'contrast':round(ratio,2),
                                'passed':ratio >= (3 if state & Gtk.StateFlags.INSENSITIVE else 4.5)})
            item.set_state_flags(original,True)
    report.write_text(json.dumps({'variant':mode,'checks':results},indent=2)+'\n')
    return False
GLib.timeout_add(500,audit)
Gtk.main()
