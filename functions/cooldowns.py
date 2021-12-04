import discord 
import datetime

class Cooldowns():

    def __init__(self):

        self.data = {}
    
    def setCooldown(self, name : str, user : discord.User):
        if name not in self.data:
            self.data[name] = {}
        
        self.data[name][str(user.id)] = datetime.datetime.now()

        return self.getCooldown(name, user)
    
    def getCooldown(self, name : str, user : discord.User):
        if name in self.data and str(user.id) in self.data[name]:
            tm = (datetime.datetime.now() - self.data[name][str(user.id)])
            return tm 
        return None 
    
    def doCooldown(self, length : datetime.timedelta, name : str, user : discord.User):
        gc = self.getCooldown(name, user)

        if gc == None or gc > length:
            self.setCooldown(name, user)
            return True 
        
        return (length - gc)