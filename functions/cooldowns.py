import discord 
import datetime

class Cooldowns():

    def __init__(self):

        self.data = {}
    
    def setCooldown(self, name : str, user : discord.User):
        """Set the cooldown for a user

        Args:
            name (str): [the section for the cooldown]
            user (discord.User): [the user to set for]

        Returns:
            [timedelta]: [The time remaining]
        """        
        if name not in self.data:
            self.data[name] = {}
        
        self.data[name][str(user.id)] = datetime.datetime.now()

        return self.getCooldown(name, user)
    
    def getCooldown(self, name : str, user : discord.User):
        """[Get the cooldwown for a user]

        Args:
            name (str): [the name of the section]
            user (discord.User): [the user to get for]

        Returns:
            [timedelta / NoneType]: [description]
        """        
        if name in self.data and str(user.id) in self.data[name]:
            tm = (datetime.datetime.now() - self.data[name][str(user.id)])
            return tm 
        return None 
    
    def doCooldown(self, length : datetime.timedelta, name : str, user : discord.User):
        """[Make and get cooldowns based on a length]

        Args:
            length (datetime.timedelta): [Length of the cooldown]
            name (str): [Cooldown section]
            user (discord.User): [The user to cooldown]

        Returns:
            [type]: [description]
        """        
        gc = self.getCooldown(name, user)

        if gc == None or gc > length:
            self.setCooldown(name, user)
            return True 
        
        return (length - gc)