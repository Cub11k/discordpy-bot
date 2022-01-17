from tinydb import TinyDB, Query
from tinydb.operations import increment, add, set
import random


class DB():

    def __init__(self, db_name, member_ids):
        self.db = TinyDB(db_name)
        self.warn = self.db.table('warn')
        self.rating = self.db.table('rating')
        self.mute = self.db.table('mute')

        User = Query()
        for member in member_ids:
            warn_users = self.warn.all()
            for user in warn_users:
                if user["id"] not in member_ids:
                    self.warn.remove(User.id == user["id"])
            rating_users = self.rating.all()
            for user in rating_users:
                if user["id"] not in member_ids:
                    self.rating.update(set("flag", 0), User.id == user["id"])
                else:
                    self.rating.update(set("flag", 1), User.id == user["id"])
            mute_users = self.mute.all()
            for user in mute_users:
                if user["id"] not in member_ids:
                    self.mute.remove(User.id == user["id"])

            if not self.warn.contains(User.id == member):
                self.warn.insert({"id": member, "warns": 0})
            if not self.rating.contains(User.id == member):
                self.rating.insert(
                    {"id": member, "text_points": 0, "voice_points": 0, "flag": 1})

    def mute_user(self, member_id, date, timer):
        User = Query()
        self.mute.upsert({"id": member_id, "date": date,
                         "timer": timer}, User.id == member_id)

    def unmute_user(self, member_id):
        User = Query()
        self.mute.remove(User.id == member_id)

    def get_mutes(self):
        return self.mute.all()

    def get_user_warns(self, member_id):
        User = Query()
        return self.warn.get(User.id == member_id)["warns"]

    def warn_user(self, member_id):
        User = Query()
        self.warn.update(increment("warns"), User.id == member_id)
        return self.get_user_warns(member_id)

    def unwarn_user(self, member_id, num: str = "all"):
        User = Query()
        warns = self.get_user_warns(member_id)
        if num == "all":
            self.warn.update({"id": member_id, "warns": 0},
                             User.id == member_id)
            return True
        try:
            num = int(num)
            self.warn.update({"id": member_id, "warns": max(0, warns - num)},
                             User.id == member_id)
            return True
        except:
            return False

    def get_warns(self):
        User = Query()
        return self.warn.search(User.warns > 0)

    def update_text_rating_user(self, member_id):
        User = Query()
        values = [0, 1, 2, 3, 4]
        weights = [0.5, 0.25, 0.125, 0.09, 0.035]
        xp = random.choices(population=values, weights=weights, k=1)
        self.rating.update(add("text_points", xp[0]), User.id == member_id)

    def update_voice_rating_user(self, member_id):
        User = Query()
        xp = 10
        self.rating.update(add("voice_points", xp), User.id == member_id)

    def get_text_rating(self):
        User = Query()
        text = self.rating.search(User.text_points > 0)
        for x in text:
            if x["flag"] == 0:
                text.remove(x)
        return text

    def set_text_rating(self, member_id, xp):
        User = Query()
        self.rating.update(set("text_points", xp), User.id == member_id)

    def get_voice_rating(self):
        User = Query()
        voice = self.rating.search(User.voice_points > 0)
        for x in voice:
            if x["flag"] == 0:
                voice.remove(x)
        return voice

    def set_voice_rating(self, member_id, xp):
        User = Query()
        self.rating.update(set("voice_points", xp), User.id == member_id)

    def remove_member(self, member_id):
        User = Query()
        self.warn.remove(User.id == member_id)
        self.rating.remove(User.id == member_id)

    def disconnect(self):
        self.db.close()


def setup_db(member_ids):
    db = DB('db.json', member_ids)
    return db
