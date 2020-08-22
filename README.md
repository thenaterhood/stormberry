# Stormberry

Configurable and extensible weather station software with
support for plugins.

Collects temperature, humidity, pressure. Calculates dewpoint.

Based on code from (Uladzislau Bayouski)[https://www.linkedin.com/in/uladzislau-bayouski-a7474111b/]

## Requirements
* Python3
* setuptools
* yapsy
* astro-pi (if using the pi-hat)

## Installation
Clone this repository, then run `sudo pip3 install -e .`. If that doesn't work or
you prefer to use the setup.py directly, you can also run `sudo python3 setup.py install`.
However, if you use the setup.py directly you will need to manually install the
requirements.

Depending on your environment, you may need to run `sudo python3 setup.py install` to install
the plugin directories.

## Configuration
By default, stormberry will run as a user (which you will need to create) called
`rouser` which is intended to be a nonprivileged user. You can change this by
overriding the service file in typical systemd fashion.

Copy the configuration file (installed as /etc/stormberry/config.ini.example or
/usr/local/etc/stormberry/config.ini.example) to config.ini in the same directory.

Options are documented directly in the file.

Stormberry provides a handful of sensor, display, and storage plugins. These are installed
by default into /lib/stormberry/plugins_available (or some permutation depending on your
system). All are disabled by default.

To enable a plugin, copy or create a symlink to its .py and .yapsy-plugin file in
/lib/stormberry/plugins_enabled (if using the default path - this directory is
configurable). To create a plugin, follow the example of any of the provided plugins
and enable it in the same way. Restart stormberry for the change to take effect.

Some of the plugins have configuration options in the main config.ini file.

## Building Plugins
stormberry uses yapsy for plugins.

To create a new plugin, you must decide if it is a display, sensor, or repository.

* A display is intended to show weather data and is called when a new reading is available.
Extend the stormberry.plugin.IDisplay class and implement its methods.
* A sensor is intended to gather data. It is periodically called, and its results are
merged with that of other sensors - beware, if you use multiple sensors at a time. Extend
the stormberry.plugin.ISensor class and implement its methods.
* A repository is for storing data and (if you like) reading it back, and is called
any time a new reading is available. Extend the
stormberry.plugin.IRepository class and implement its methods.

If you have plugins that need to share a resource (in the provided plugins, the
Pi Sense Hat plugins for sensors and display are separate, but share the hat), there
is a plugin data manager. It's passed to your plugin in the activate method and
has methods for setting and getting objects.

The "universal" object that plugins must understand is the WeatherReading object.
Plugins don't need to use or understand all the fields, so if you're adding a new
type of sensor, you may need to expand the data storage plugins you're interested
in to store your data.

You may use your own configuration file (you will need to load it yourself) or
add options to the main stormberry file - placing them in their own section is
recommended. The main stormberry configuration is passed to your plugin
class and will be available in `self.config` automatically.

See the Configuration section for how to enable your plugin.
