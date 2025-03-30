import time

import redis
import random

class InsultServer:
    def __init__(self, queue_name, client=None):
        self.subscribers = []
        self.insultList = [
            "You're a fucking idiot.",
            "You're a worthless loser.",
            "You're dumber than a bag of rocks.",
            "You're such an asshole, even mirrors hate reflecting you.",
            "You're a pathetic excuse for a human being.",
            "You're a total dumbass.",
            "You're an absolute moron.",
            "You're as useless as a broken condom.",
            "You're a disgrace to common sense.",
            "You're a brain-dead waste of space.",
            "You're as worthless as a wet matchstick.",
            "You're the human embodiment of trash.",
            "You're a clueless idiot.",
            "You're so dumb, even Google gives up on you.",
            "You're a fucking failure.",
            "You're a fucking joke.",
            "You're as sharp as a marble, dumbass.",
            "You're a bitchy little clown.",
            "You're about as useful as a screen door on a submarine, moron.",
            "You're a useless sack of shit.",
            "You're a nitwit with the IQ of a potato.",
            "You're as smart as a brick, asshole.",
            "You're an ignorant clown.",
            "You're a jerk with the charm of roadkill.",
            "You're as braindead as a zombie on vacation.",
            "You're so dumb, you’d drown in a kiddie pool.",
            "You're a fucking disgrace.",
            "You're about as necessary as a pogo stick on a tightrope, loser.",
            "You're an imbecile with the personality of moldy bread.",
            "You're a fucking clown, and not even the funny kind.",
            "You're as stupid as a rock, just less useful.",
            "You're a joke that no one laughs at, bitch.",
            "You're a worthless piece of garbage.",
            "You're so dumb, you try to climb a broken escalator.",
            "You're an embarrassment to stupidity itself, moron.",
            "You're a braindead waste of time.",
            "You're so clueless, even Siri ignores you.",
            "You're a total jackass, and that's an insult to donkeys.",
            "You're a failure at failing, dumbass.",
            "You're an idiot with a master’s degree in bullshit.",
            "You're the definition of pathetic.",
            "You're as smart as a doorknob, asshole.",
            "You're the reason warning labels exist, dumbass.",
            "You're a clown at a funeral—completely out of place and unwanted.",
            "You're a disgrace to basic intelligence.",
            "You're a brain-dead nitwit with zero redeeming qualities.",
            "You're a fucking trainwreck.",
            "You're an ignorant twit with no hope of improvement.",
            "You're an asshole, plain and simple.",
            "You're a joke that even bad comedians wouldn’t tell.",
            "You're a total waste of oxygen, loser.",
            "You're so fucking clueless, it's almost impressive.",
            "You're the human equivalent of a rejected meme.",
            "You're as useful as a trapdoor on a lifeboat, idiot.",
            "You're a moron with the common sense of a goldfish.",
            "You're a walking example of why intelligence tests should be mandatory.",
            "You're a failure wrapped in disappointment.",
            "You're a braindead disgrace to logic.",
            "You're as dumb as a rock but with less personality.",
            "You're a fucking embarrassment.",
            "You're the dictionary definition of worthless.",
            "You're a total dumbass, and that’s putting it nicely.",
            "You're a failure at everything, even being decent.",
            "You're as ignorant as they come, asshole.",
            "You're an imbecile with no hope for change.",
            "You're a clown in a world that doesn’t want a circus.",
            "You're as smart as expired milk, dumbass.",
            "You're a nitwit with the charm of a dumpster fire.",
            "You're a worthless joke of a human being.",
            "You're so brain-dead, even zombies wouldn't want you.",
            "You're an idiot who makes bad decisions look smart.",
            "You're a disgrace to the concept of intelligence.",
            "You're a failure at being a decent person.",
            "You're as sharp as a spoon, moron.",
            "You're a fucking waste of space.",
            "You're the human version of a deleted file, useless and forgotten.",
            "You're a fucking idiot with no redeeming qualities.",
            "You're so dumb, you’d trip on a cordless phone.",
            "You're as intelligent as a bag of hammers, asshole.",
            "You're a clueless twit with the wisdom of a toddler.",
            "You're the opposite of useful, dumbass.",
            "You're a loser with no winning qualities.",
            "You're an ignorant sack of wasted potential.",
            "You're a braindead clown with no act.",
            "You're as stupid as a screen door on a spaceship.",
            "You're a total fucking disaster.",
            "You're a joke that even a bad punchline wouldn't save.",
            "You're an imbecile who confuses stupidity with confidence.",
            "You're a disgrace to common sense, asshole.",
            "You're a failure even at being funny, dumbass.",
            "You're as welcome as a fart in an elevator, idiot.",
            "You're a worthless waste of energy.",
            "You're the reason the phrase 'bless your heart' exists.",
            "You're as necessary as an ashtray on a motorcycle, loser.",
            "You're a complete waste of time, asshole.",
            "You're as dumb as a screen saver, but at least those change occasionally.",
            "You're the human version of a deleted file, useless and forgotten.",
            "You're a fucking idiot with no redeeming qualities.",
            "You're so dumb, you’d trip on a cordless phone.",
            "You're as intelligent as a bag of hammers, asshole."
        ]

        self.blacklist = [
            "fuck", "bitch", "asshole", "idiot", "moron", "stupid", "dumb", "loser",
            "jerk", "clown", "trash", "pathetic", "worthless", "useless", "disgrace",
            "failure", "imbecile", "ignorant", "braindead", "clueless", "dunce", "nitwit"
        ]

        # Connect to Redis
        self.client = client if client else redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.queue_name = queue_name
        print("ConsumerFilter is working...")

    def filter_insult(self, message):
        print(f"Insult Received: {message}")  # Debugging

        words = message.split()  # Split message into words
        filtered_words = [
            "CENSORED" if word.lower().strip(".,!?") in (insult.lower() for insult in self.blacklist) else word
            for word in words
        ]

        censored_message = " ".join(filtered_words)
        print(f" [x] Received and censored message: {censored_message}")
        return censored_message

    def add_text(self):
        insult = self.filter_insult(random.choice(self.insultList))
        self.client.lpush(self.queue_name, insult)

    def get_insults(self):
        return self.insultList

    def insult_me(self):
        self.client.rpush(self.queue_name, random.choice(self.insultList))


def start_server(queue_name, stop_event):
    insult_serv = InsultServer(queue_name)
    while not stop_event.is_set():
        insult_serv.add_text()
        time.sleep(0.1)
