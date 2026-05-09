import wx
import config
import gui
from gui.settingsDialogs import SettingsPanel

CONFIG_SECTION = "contextLabeler"
CONFIG_SPEC = {
    "apiKey": "string(default='')",
    "logClassifications": "boolean(default=False)",
}

config.conf.spec[CONFIG_SECTION] = CONFIG_SPEC


def get_api_key() -> str:
    return config.conf[CONFIG_SECTION]["apiKey"]


def get_log_classifications() -> bool:
    return config.conf[CONFIG_SECTION]["logClassifications"]


class ContextLabelerPanel(SettingsPanel):
    title = "Context Labeler"

    def makeSettings(self, settingsSizer):
        sizer = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        self._apiKey = sizer.addLabeledControl("Anthropic API key:", wx.TextCtrl)
        self._apiKey.SetValue(config.conf[CONFIG_SECTION]["apiKey"])
        self._logToggle = sizer.addItem(wx.CheckBox(self, label="Log classifications to NVDA log"))
        self._logToggle.SetValue(config.conf[CONFIG_SECTION]["logClassifications"])

    def onSave(self):
        config.conf[CONFIG_SECTION]["apiKey"] = self._apiKey.GetValue()
        config.conf[CONFIG_SECTION]["logClassifications"] = self._logToggle.GetValue()
