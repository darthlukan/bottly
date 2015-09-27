############ ###user # add pokemon ##
    if self.trigger + 'gamer' == command:
        if self.is_admin(sender):
            try:
                channel = data[4]
            except IndexError:
                pass
            gamer = self.gamer(sender, message)
            self.send_message(channel, sender, '.. You Choose', message)
        else:
            self.deny_command(channel, sender)



    def gamer(sender, message):
        db = self.db
        database.save_gamer(db, sender, message)
        return

######################
    def gamer(sender, message):
        db = self.db
        database.save_gamer(db, sender, message)
        return
