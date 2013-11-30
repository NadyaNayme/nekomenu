nekomenu
========

Nekomenu is a dynamic, auto-updated applications menu for openbox desktops.

### How to install?

```
wget https://raw.github.com/ansdor/nekomenu/master/nekomenu.py
chmod +x nekomenu.py
sudo mv nekomenu.py /usr/bin/nekomenu
```

Then add a line to your `~/.config/openbox/menu.xml` containing `<menu execute="nekomenu" id="NekoMenu" label="Neko Menu"/>`
