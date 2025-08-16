# -*- coding: utf-8 -*-

"""
Study Bot Plugins Package

This package contains all the plugins for the Study Bot functionality.
"""

__version__ = "1.0.0"
__author__ = "Study Bot Team"
__description__ = "Study Bot Plugins Package"

# Import all plugins
from . import study_bot
from . import content_bot
from . import pm_filter
from . import command
from . import admin
from . import file_upload
from . import help
from . import index
from . import route
from . import channel
from . import broadcast
from . import banned
from . import join_req
from . import misc
from . import Premium
from . import keep_alive
from . import check_expired_premium
from . import web_server

# Plugin registry
PLUGINS = [
    study_bot,
    content_bot,
    pm_filter,
    command,
    admin,
    file_upload,
    help,
    index,
    route,
    channel,
    broadcast,
    banned,
    join_req,
    misc,
    Premium,
    keep_alive,
    check_expired_premium,
    web_server,
]

def get_plugin(name):
    """Get plugin by name"""
    for plugin in PLUGINS:
        if plugin.__name__ == name:
            return plugin
    return None

def list_plugins():
    """List all available plugins"""
    return [plugin.__name__ for plugin in PLUGINS]

def reload_plugin(name):
    """Reload a specific plugin"""
    plugin = get_plugin(name)
    if plugin:
        import importlib
        importlib.reload(plugin)
        return True
    return False
