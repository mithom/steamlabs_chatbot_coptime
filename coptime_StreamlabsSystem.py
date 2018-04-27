import clr

clr.AddReference('IronPython.Modules.dll')
import os
import codecs
import json
import time

ScriptName = "coptime"
Website = "https://www.Streamlabs.Chatbot.com"
Description = "rewards the users based on time since last specified emote used"
Creator = "mi_thom"
Version = "1.0.0"

ScriptSettings = None
m_SettingsFile = os.path.join(os.path.dirname(__file__), "coptimeSettings.json")
m_ModeratorPermission = "Moderator"
m_allowed_permissions = ["Everyone", "Regular", "Subscriber", "GameWisp_Subscriber", "User_Specific", "Min_Rank",
                         "Min_Points", "Min_Hours", "Moderator", "Editor", "Caster"]
m_timestamp = 0


class Settings(object):
    def __init__(self, settings_file):
        try:
            with codecs.open(settings_file, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            self.emote = "Kappa"
            self.min_time = 60
            self.user_cd = 0
            self.global_cd = 0

            # costs & rewards
            self.cost = 0
            self.reward = 0
            self.reward_global = True
            self.send_warning = True

            # command names
            self.cop_command = "!coptime"
            self.currency_name = "points"

            # responses
            self.success_resp = "{0}, the emote {1} has been used within the last {2} seconds. all users have been rewarded {3} {4}"
            self.fail_resp = "{0}, the emote {0} has not been used within the last {2} seconds. it cost hem {3} {4}"
            self.warning_resp = "{0} does not have enough {1} to use this command"

    def reload(self, jsonData):
        self.__dict__ = json.loads(jsonData, encoding="utf-8")

    def save(self, settings_file):
        try:
            with codecs.open(settings_file, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(settings_file.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return


# ---------------------------------------
#   [required] initializing the script
# ---------------------------------------
def Init():
    global ScriptSettings
    ScriptSettings = Settings(m_SettingsFile)


def Execute(data):
    if data.IsChatMessage():  # not a whisper or random packet
        if not data.IsFromDiscord():
            message = data.Message
            user = data.User
            check_emote(message)
            p_count = data.GetParamCount()
            if p_count == 1:
                param1 = data.GetParam(0)
                if param1 == ScriptSettings.cop_command:
                    cop_command(user)


def cop_command(user):
    current_time = time.clock()
    if not (Parent.IsOnCooldown(ScriptName, "copCommand") and Parent.IsOnUserCooldown(ScriptName, "copCommand", user)):
        Parent.AddCooldown(ScriptName, "copCommand", ScriptSettings.global_cd)
        Parent.AddUserCooldown(ScriptName, "copCommand", user, ScriptSettings.user_cd)
        if Parent.GetPoints(user) > ScriptSettings.cost:
            if (current_time - m_timestamp) > ScriptSettings.min_time:
                to_send = "/me "
                to_send += ScriptSettings.success_resp.format(user, ScriptSettings.emote, ScriptSettings.min_time,
                                                              ScriptSettings.reward, ScriptSettings.currency_name)
                Parent.SendStreamMessage(to_send)
                if ScriptSettings.reward_global:
                    data = {user: ScriptSettings.reward for user in Parent.GetViewerList()}
                    Parent.AddPointsAllAsync(data, empty)
                else:
                    Parent.AddPoints(user, ScriptSettings.reward)
            else:
                Parent.RemovePoints(user, ScriptSettings.cost)
                to_send = "/me " + ScriptSettings.fail_resp.format(user, ScriptSettings.emote, ScriptSettings.min_time,
                                                                   ScriptSettings.cost, ScriptSettings.currency_name)
                Parent.SendStreamMessage(to_send)
        else:
            if ScriptSettings.send_warning:
                Parent.SendStreamMessage(
                    "/me " + ScriptSettings.warning_resp.format(user, ScriptSettings.currency_name))


def empty():
    pass


def check_emote(message):
    global m_timestamp
    if ScriptSettings.emote in message:
        m_timestamp = time.clock()


def Tick():
    pass


def Unload():
    ScriptSettings.save(m_SettingsFile)


def ReloadSettings(jsonData):
    ScriptSettings.reload(jsonData)
