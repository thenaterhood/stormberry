# Stormberry

Configurable and extensible Raspberry Pi weather station software with
support for plugins.

Collects temperature, humidity, pressure. Calculates dewpoint.

Based on code from (Uladzislau Bayouski)[https://www.linkedin.com/in/uladzislau-bayouski-a7474111b/]

## Requirements
* Python3
* setuptools
* yapsy
* astro-pi

## Installation
Clone this repository, then run `sudo pip3 install -e .`. If that doesn't work or
you prefer to use the setup.py directly, you can also run `sudo python3 setup.py install`.
However, if you use the setup.py directly you will need to manually install the
requirements.

## Configuration
The stormberry configuration file can be found at either /etc/stormberry/config.ini
or /usr/local/etc/stormberry/config.ini depending on your system.
Options are documented directly in the file.

Plugins can be enabled by placing them (the .py and the .yapsy-plugin files) in
/usr/local/lib/stormberry/plugins. There are no plugins enabled by default - you can
copy them from the `plugins` directory (or from
/usr/local/lib/python3.5/dist-packages/stormberry/plugin_examples). Plugins
shipped with stormberry include a Wunderground uploader, CSV file creator, and
a SQLite database writer.

If that directory does not exist, feel free to create it or update the config
file to use a different plugin directory.

## Building Plugins
stormberry uses yapsy for plugins.

To create a new plugin class, you must extend both `stormberry.GenericPlugin.GenericPlugin`
and `yapsy.IPlugin.IPlugin`. Make sure to implement the methods in the stormberry
GenericPlugin interface. You will also need to create a yapsy-plugin info file
for your plugin (examples are available in the `plugins` directory).

You may use your own configuration file (you will need to load it yourself) or
add options to the main stormberry file - placing them in their own section is
recommended. The main stormberry configuration is passed to your plugin
class and will be available in `self.config` automatically.

See the Configuration section for how to enable your plugin.
