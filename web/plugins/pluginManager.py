import constants


class PluginManager:
    def __init__(self, app, translator):
        self.app = app
        self.translator = translator
        self.plugins = {}

    def load_plugin(self, menu_name: str) -> None:
        """
        Load a plugin
        :param menu_name:  The name of the plugin to load.
        :return:  None
        """
        if menu_name in constants.PLUGINS:
            # Load and initialize the plugin
            plugin = self.app.plugin_classes[menu_name](self.app)
            plugin.initialize()
            menu = self.app.menubar.addMenu(self.translator.get_translation(menu_name))
            menu.addActions(plugin.get_menu_items())
            self.plugins[menu_name] = plugin

    def load_plugins(self) -> None:
        """
        Load all plugins
        :return:  None
        """
        for menu_name in self.app.plugin_classes.keys():
            self.load_plugin(menu_name)
