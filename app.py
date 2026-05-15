from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json, os, random, hashlib
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "eduable-2024-secret"
DB = os.path.join(os.path.dirname(__file__), "data.json")

def load_db():
    if os.path.exists(DB):
        with open(DB) as f: return json.load(f)
    return {"users": {}}

def save_db(d):
    with open(DB, "w") as f: json.dump(d, f, indent=2)

QUIZ = {
    "Animals": {
        "Beginner": [
            {"q":"Which animal says Woof?","visual":"🐶","hint":"Think about a pet that wags its tail!","choices":["🐶 Dog","🐱 Cat","🐮 Cow","🐸 Frog"],"a":"🐶 Dog"},
            {"q":"Which animal has a trunk?","visual":"🐘","hint":"This animal is very big and grey!","choices":["🦁 Lion","🐘 Elephant","🐧 Penguin","🐰 Rabbit"],"a":"🐘 Elephant"},
            {"q":"Which animal hops?","visual":"🐰","hint":"This fluffy animal loves carrots!","choices":["🐶 Dog","🐱 Cat","🐰 Rabbit","🐟 Fish"],"a":"🐰 Rabbit"},
            {"q":"Which animal lives in water?","visual":"🐟","hint":"This animal swims and has fins!","choices":["🐶 Dog","🐟 Fish","🐱 Cat","🐰 Rabbit"],"a":"🐟 Fish"},
        ],
        "Intermediate": [
            {"q":"Which animal is the king of the jungle?","visual":"🦁","hint":"This animal has a big fluffy mane!","choices":["🐘 Elephant","🦒 Giraffe","🦁 Lion","🐬 Dolphin"],"a":"🦁 Lion"},
            {"q":"Which bird loves to swim?","visual":"🐧","hint":"This black and white bird lives in cold places!","choices":["🦅 Eagle","🦜 Parrot","🐧 Penguin","🦆 Duck"],"a":"🐧 Penguin"},
            {"q":"Which animal has a very long neck?","visual":"🦒","hint":"This animal can eat leaves from tall trees!","choices":["🦁 Lion","🐧 Penguin","🐘 Elephant","🦒 Giraffe"],"a":"🦒 Giraffe"},
            {"q":"Which animal makes honey?","visual":"🐝","hint":"This small insect buzzes and lives in a hive!","choices":["🦋 Butterfly","🐝 Bee","🐛 Caterpillar","🐞 Ladybug"],"a":"🐝 Bee"},
        ],
        "Advanced": [
            {"q":"What is the fastest land animal?","visual":"🐆","hint":"This spotted cat can run up to 70 mph!","choices":["🦁 Lion","🐆 Cheetah","🐎 Horse","🐺 Wolf"],"a":"🐆 Cheetah"},
            {"q":"What is a group of wolves called?","visual":"🐺","hint":"Think of a word that means a group working together!","choices":["Herd","Flock","Pack","Pride"],"a":"Pack"},
            {"q":"Which animal can change its colour?","visual":"🦎","hint":"This reptile blends into its surroundings!","choices":["🐊 Crocodile","🦎 Chameleon","🐍 Snake","🦖 Dinosaur"],"a":"🦎 Chameleon"},
            {"q":"What is a baby kangaroo called?","visual":"🦘","hint":"It lives in its mum's pouch!","choices":["Cub","Joey","Pup","Foal"],"a":"Joey"},
        ],
    },
    "Colours": {
        "Beginner": [
            {"q":"What colour is the sky?","visual":"🌤️","hint":"Look up on a sunny day — what do you see?","choices":["🔴 Red","🔵 Blue","🟡 Yellow","🟢 Green"],"a":"🔵 Blue"},
            {"q":"What colour is the sun?","visual":"☀️","hint":"This colour is bright and warm like sunshine!","choices":["🔵 Blue","🟠 Orange","🟡 Yellow","🔴 Red"],"a":"🟡 Yellow"},
            {"q":"What colour is grass?","visual":"🌿","hint":"This is the colour of plants and trees!","choices":["🟢 Green","🔵 Blue","🟡 Yellow","🟠 Orange"],"a":"🟢 Green"},
            {"q":"What colour is a strawberry?","visual":"🍓","hint":"This colour is the same as fire engines!","choices":["🟡 Yellow","🔵 Blue","🔴 Red","🟢 Green"],"a":"🔴 Red"},
        ],
        "Intermediate": [
            {"q":"What colour do you get mixing blue and yellow?","visual":"🎨","hint":"Think of the colour of leaves and frogs!","choices":["🟣 Purple","🟢 Green","🟠 Orange","🩷 Pink"],"a":"🟢 Green"},
            {"q":"What colour is a flamingo?","visual":"🦩","hint":"This colour is light red, like a rose!","choices":["🔴 Red","🟠 Orange","🩷 Pink","🟣 Purple"],"a":"🩷 Pink"},
            {"q":"What colour is a pumpkin?","visual":"🎃","hint":"This colour is between red and yellow!","choices":["🟡 Yellow","🟠 Orange","🔴 Red","🟢 Green"],"a":"🟠 Orange"},
            {"q":"What colour is a grape?","visual":"🍇","hint":"This colour is a mix of red and blue!","choices":["🔵 Blue","🔴 Red","🟣 Purple","🟢 Green"],"a":"🟣 Purple"},
        ],
        "Advanced": [
            {"q":"What colour do you get mixing red and white?","visual":"🎨","hint":"Think of a soft, light version of red!","choices":["🟠 Orange","🩷 Pink","🟣 Purple","🔴 Red"],"a":"🩷 Pink"},
            {"q":"What colour is turquoise?","visual":"💎","hint":"This colour is between blue and green, like the ocean!","choices":["Blue-Green","Red-Orange","Yellow-Purple","Pink-White"],"a":"Blue-Green"},
            {"q":"What are the three primary colours?","visual":"🎨","hint":"These are the colours you cannot make by mixing others!","choices":["Red, Blue, Yellow","Red, Green, Purple","Orange, Blue, Pink","Black, White, Grey"],"a":"Red, Blue, Yellow"},
            {"q":"What colour is indigo?","visual":"🌈","hint":"It is between blue and violet in the rainbow!","choices":["Light Blue","Dark Blue-Purple","Bright Green","Deep Red"],"a":"Dark Blue-Purple"},
        ],
    },
    "Shapes": {
        "Beginner": [
            {"q":"How many sides does a triangle have?","visual":"🔺","hint":"Count the sides of a pizza slice!","choices":["2","3","4","5"],"a":"3"},
            {"q":"What shape is a ball?","visual":"⚽","hint":"This shape is perfectly round with no corners!","choices":["Square","Triangle","Circle","Rectangle"],"a":"Circle"},
            {"q":"How many sides does a square have?","visual":"🟥","hint":"Think of a window or a picture frame!","choices":["3","4","5","6"],"a":"4"},
            {"q":"What shape is a door?","visual":"🚪","hint":"This shape is taller than it is wide!","choices":["Circle","Triangle","Square","Rectangle"],"a":"Rectangle"},
        ],
        "Intermediate": [
            {"q":"How many sides does a pentagon have?","visual":"⬠","hint":"Penta means five in Greek!","choices":["4","5","6","7"],"a":"5"},
            {"q":"What shape is a stop sign?","visual":"🛑","hint":"Count the sides — it has more than 6!","choices":["Hexagon","Octagon","Pentagon","Heptagon"],"a":"Octagon"},
            {"q":"What shape is an egg?","visual":"🥚","hint":"This shape is like a stretched circle!","choices":["Circle","Oval","Rectangle","Triangle"],"a":"Oval"},
            {"q":"How many corners does a triangle have?","visual":"🔺","hint":"Same as the number of sides!","choices":["2","3","4","5"],"a":"3"},
        ],
        "Advanced": [
            {"q":"What is a 3D square called?","visual":"🎲","hint":"Think of a dice or a box!","choices":["Prism","Pyramid","Cube","Sphere"],"a":"Cube"},
            {"q":"What is a 3D circle called?","visual":"🌍","hint":"Think of a ball or the Earth!","choices":["Cylinder","Cone","Cube","Sphere"],"a":"Sphere"},
            {"q":"How many sides does a hexagon have?","visual":"⬡","hint":"Hex means six in Greek!","choices":["5","6","7","8"],"a":"6"},
            {"q":"What shape has no corners at all?","visual":"⭕","hint":"This shape goes round and round forever!","choices":["Oval","Triangle","Circle","Square"],"a":"Circle"},
        ],
    },
    "Numbers": {
        "Beginner": [
            {"q":"What is 1 + 1?","visual":"1️⃣➕1️⃣","hint":"Hold up one finger on each hand — how many total?","choices":["1","2","3","4"],"a":"2"},
            {"q":"How many fingers on one hand?","visual":"✋","hint":"Count the fingers on your hand!","choices":["4","5","6","3"],"a":"5"},
            {"q":"What comes after 4?","visual":"4️⃣","hint":"Count: 1, 2, 3, 4, ...?","choices":["3","6","5","7"],"a":"5"},
            {"q":"How many eyes do you have?","visual":"👀","hint":"Look in a mirror - count your eyes!","choices":["1","2","3","4"],"a":"2"},
        ],
        "Intermediate": [
            {"q":"What is 5 + 3?","visual":"5️⃣➕3️⃣","hint":"Count 5 fingers, then 3 more!","choices":["7","8","9","6"],"a":"8"},
            {"q":"What is 10 - 4?","visual":"🔟➖4️⃣","hint":"Start at 10 and count back 4 steps!","choices":["5","6","7","8"],"a":"6"},
            {"q":"How many days in a week?","visual":"📅","hint":"Monday, Tuesday... count all the days!","choices":["5","6","7","8"],"a":"7"},
            {"q":"What is 3 x 2?","visual":"3️⃣✖️2️⃣","hint":"3 groups of 2 — count them all!","choices":["4","5","6","7"],"a":"6"},
        ],
        "Advanced": [
            {"q":"What is 12 ÷ 3?","visual":"🔢","hint":"How many groups of 3 fit into 12?","choices":["3","4","5","6"],"a":"4"},
            {"q":"What is 7 x 4?","visual":"7️⃣✖️4️⃣","hint":"7 groups of 4 — add them up!","choices":["24","28","32","21"],"a":"28"},
            {"q":"What is 25 - 8?","visual":"🔢","hint":"Start at 25 and count back 8!","choices":["15","16","17","18"],"a":"17"},
            {"q":"What is half of 20?","visual":"🔢","hint":"Split 20 into two equal groups!","choices":["8","9","10","11"],"a":"10"},
        ],
    },
    "Language": {
        "Beginner": [
            {"q":"What do you say when you want something politely?","visual":"🙏","hint":"This magic word shows good manners!","choices":["Sorry","Hello","Please","Goodbye"],"a":"Please"},
            {"q":"What do you say when someone helps you?","visual":"💛","hint":"This shows you are grateful!","choices":["Sorry","Thank You","Hello","Please"],"a":"Thank You"},
            {"q":"What do you say when you meet someone?","visual":"👋","hint":"This is how we greet people!","choices":["Goodbye","Sorry","Thank You","Hello"],"a":"Hello"},
            {"q":"What do you say when you make a mistake?","visual":"😔","hint":"This word shows you care about others' feelings!","choices":["Hello","Please","Thank You","Sorry"],"a":"Sorry"},
        ],
        "Intermediate": [
            {"q":"What letter does 'Elephant' start with?","visual":"🐘","hint":"The first letter of Elephant — say it out loud!","choices":["A","E","I","O"],"a":"E"},
            {"q":"How many vowels are in the alphabet?","visual":"🔤","hint":"A, E, I, O, U — count them!","choices":["4","5","6","7"],"a":"5"},
            {"q":"What is the middle letter of CAT?","visual":"🐱","hint":"C - ? - T — what goes in the middle?","choices":["C","A","T","E"],"a":"A"},
            {"q":"What letter does 'Sun' start with?","visual":"☀️","hint":"Say Sun slowly — what is the first sound?","choices":["C","Z","S","X"],"a":"S"},
        ],
        "Advanced": [
            {"q":"How many letters are in the alphabet?","visual":"🔤","hint":"Count from A all the way to Z!","choices":["24","25","26","27"],"a":"26"},
            {"q":"What is the 10th letter of the alphabet?","visual":"🔤","hint":"A=1, B=2, C=3... keep counting to 10!","choices":["I","J","K","H"],"a":"J"},
            {"q":"Which word is a noun?","visual":"📝","hint":"A noun is a person, place, or thing!","choices":["Run","Happy","Apple","Quickly"],"a":"Apple"},
            {"q":"Which sentence is correct?","visual":"📝","hint":"Think about which one sounds right!","choices":["She go to school","She goes to school","She going school","She gone school"],"a":"She goes to school"},
        ],
    },
}

BUDDIES = {
    "Cosmo":   {"color":"#6EC6FF","bg":"#E8F4FF","face":"🤖","style":"cosmo"},
    "Luna":    {"color":"#FFB6D9","bg":"#FFE8F5","face":"🧚","style":"luna"},
    "Rex":     {"color":"#7ED87E","bg":"#E8FFE8","face":"🦕","style":"rex"},
    "Captain": {"color":"#4169E1","bg":"#E8EEFF","face":"🦸","style":"captain"},
    "Sunny":   {"color":"#FF9F43","bg":"#FFF0E0","face":"🦊","style":"sunny"},
    "Bubbles": {"color":"#B388FF","bg":"#F0E6FF","face":"🐙","style":"bubbles"},
    "Blaze":   {"color":"#FF6B6B","bg":"#FFE8E8","face":"🐉","style":"blaze"},
    "Pip":     {"color":"#333333","bg":"#E8F4FF","face":"🐧","style":"pip"},
    "Lumi":    {"color":"#81C784","bg":"#E8F5E9","face":"🤖","style":"lumi"},
    "Buddy Bear": {"color":"#D4A574","bg":"#FFF3E0","face":"🐻","style":"bear"},
    "Mia":     {"color":"#FFB6C1","bg":"#FFF0F5","face":"🐰","style":"mia"},
    "Zara":    {"color":"#333333","bg":"#F5F5F5","face":"🦓","style":"zara"},
}

BUDDY_HINTS = {
    "Cosmo":   ["Beep boop! Let me scan again... try another answer!","My circuits say you are so close!","Look at the picture — the answer is there!"],
    "Luna":    ["Almost, darling! Sprinkle some more thought!","You are so close! The magic is in you!","Look at the picture for a sparkly clue!"],
    "Rex":     ["RAWR! So close! Give it another try!","You are doing great! Think one more time!","The picture has a clue — look carefully!"],
    "Captain": ["Almost there, cadet! Try another approach!","Think strategically — you can do this!","Check the visual clue, soldier!"],
    "Sunny":   ["Ooh so close! My tail is wagging — try again!","Think about it — I know you know this!","The picture is your clue, friend!"],
    "Bubbles": ["Splish! Almost! Let the answer float to you!","You are so close! Think deep!","Look at the picture for a watery clue!"],
    "Blaze":   ["Whoosh! So close! Let me warm up your thinking!","You are almost there! Think fiery thoughts!","The picture has a hot clue!"],
    "Pip":     ["Waddle waddle! Almost! Try another answer!","You are so close! Think cool thoughts!","The picture is your icy clue!"],
    "Lumi":    ["Hmm, almost! Let me light the way — try again!","You are so close! I believe in you!","Look at the picture for a glowing clue!"],
    "Buddy Bear": ["Almost there, friend! Give it another try!","You are so close! Think carefully!","The picture has a cozy clue!"],
    "Mia":     ["Hop hop! So close! Try one more time!","You are almost there! Think bunny thoughts!","The picture has a fluffy clue!"],
    "Zara":    ["Almost! Let me gallop to the answer with you!","You are so close! Think about it!","The picture has a stripy clue!"],
}

BUDDY_PRAISE = {
    "Cosmo":   ["BEEP BOOP! Correct! My circuits are overjoyed!","Processing... GENIUS DETECTED!","You are absolutely brilliant, human friend!"],
    "Luna":    ["Magical! Absolutely sparkling answer!","You are a star! Fairy dust everywhere!","Wonderful! The magic is strong in you!"],
    "Rex":     ["RAWR! That is AMAZING! You are so smart!","Dino-mite answer! I am so proud!","You are the smartest friend ever!"],
    "Captain": ["Mission accomplished! Outstanding work, cadet!","Star Command confirms: GENIUS!","That is exactly right! Stellar work!"],
    "Sunny":   ["YIP YIP! Brilliant! My tail is wagging so fast!","You are SO clever! I knew you could do it!","Fantastic! You are amazing!"],
    "Bubbles": ["SPLASH! Correct! The ocean celebrates you!","Brilliant! You are deeper than the sea!","Wonderful! Waves of genius!"],
    "Blaze":   ["WHOOSH! Fire of knowledge! You got it!","Blazing brilliant! That is correct!","You are on FIRE! Amazing answer!"],
    "Pip":     ["WADDLE YEAH! You got it! So cool!","Ice cold perfect! You are amazing!","Penguin approved! Brilliant answer!"],
    "Lumi":    ["Glowing with pride! You got it right!","Brilliant! You light up my circuits!","Amazing! You are a shining star!"],
    "Buddy Bear": ["Bear hug! That is correct!","Honey sweet answer! You are amazing!","Paws up! Brilliant work, friend!"],
    "Mia":     ["Hop hop hooray! You got it!","Bunny brilliant! That is perfect!","Carrot-level genius! Amazing!"],
    "Zara":    ["Galloping great! You got it right!","Stripe-tastic answer! Well done!","Zebra approved! You are amazing!"],
}

TOPIC_META = {
    "Animals":  {"emoji":"🐯","color":"#FFD6B0","text_color":"#8B4513"},
    "Colours":  {"emoji":"🎨","color":"#F0D6F5","text_color":"#6B2D8B"},
    "Shapes":   {"emoji":"⭐","color":"#C8E6FA","text_color":"#1A5276"},
    "Numbers":  {"emoji":"🔢","color":"#C8F0D6","text_color":"#1A6B3C"},
    "Language": {"emoji":"📖","color":"#FFF3C8","text_color":"#7D6608"},
}

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        role     = request.form.get("role","child")
        if not username: return render_template("login.html", error="Please enter a username")
        db = load_db()
        if username not in db["users"]:
            db["users"][username] = {
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "role": role, "buddy": "Cosmo",
                "sessions": [], "badges": [], "topics_tried": [],
                "difficulty": {t:"Beginner" for t in TOPIC_META}
            }
            save_db(db)
        session["user"]  = username
        session["role"]  = role
        user = db["users"][username]
        session["buddy"] = user.get("buddy","Cosmo")
        if user.get("chosen_language"):
            session["chosen_language"] = user["chosen_language"]
        if role in ("guardian","teacher"):
            return redirect(url_for("guardian"))
        # Go to mood selection first
        return redirect(url_for("mood"))
    return render_template("login.html")

@app.route("/choose_buddy")
def choose_buddy():
    if "user" not in session: return redirect(url_for("login"))
    next_page = request.args.get("next", "home")
    topic = request.args.get("topic", "Animals")
    return render_template("choose_buddy.html", username=session["user"],
                           next_page=next_page, topic=topic)

@app.route("/logout")
def logout():
    # Reset buddy_chosen so they pick again next login
    if "user" in session:
        db = load_db()
        if session["user"] in db["users"]:
            db["users"][session["user"]]["buddy_chosen"] = False
            save_db(db)
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "user" not in session: return redirect(url_for("login"))
    db   = load_db()
    user = db["users"].get(session["user"], {})
    buddy_key  = user.get("buddy","Cosmo")
    buddy_data = BUDDIES.get(buddy_key, BUDDIES["Cosmo"])
    difficulty = user.get("difficulty", {t:"Beginner" for t in TOPIC_META})
    return render_template("home.html", username=session["user"],
                           topics=TOPIC_META, buddy=buddy_key,
                           buddy_data=buddy_data, buddies=BUDDIES,
                           difficulty=difficulty)

@app.route("/mood")
def mood():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("mood.html", username=session["user"])

@app.route("/set_mood", methods=["POST"])
def set_mood():
    if "user" not in session: return jsonify({"error":"not logged in"})
    data = request.get_json()
    mood = data.get("mood", "happy")
    db = load_db()
    db["users"][session["user"]]["mood"] = mood
    import datetime
    db["users"][session["user"]].setdefault("mood_history",[]).append({"mood":mood,"date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    # Keep only last 30 entries
    db["users"][session["user"]]["mood_history"] = db["users"][session["user"]]["mood_history"][-30:]
    save_db(db)
    session["mood"] = mood
    return jsonify({"status":"ok"})

@app.route("/set_buddy", methods=["POST"])
def set_buddy():
    if "user" not in session: return jsonify({"error":"not logged in"})
    buddy = request.get_json().get("buddy","Cosmo")
    db = load_db()
    db["users"][session["user"]]["buddy"] = buddy
    db["users"][session["user"]]["buddy_chosen"] = True
    save_db(db)
    session["buddy"] = buddy
    session["buddy_picked"] = True
    return jsonify({"status":"ok", "buddy_data": BUDDIES.get(buddy, BUDDIES["Lumi"])})

@app.route("/set_difficulty", methods=["POST"])
def set_difficulty():
    if "user" not in session: return jsonify({"error":"not logged in"})
    data = request.get_json()
    topic = data.get("topic")
    level = data.get("level","Beginner")
    db = load_db()
    db["users"][session["user"]].setdefault("difficulty",{})[topic] = level
    save_db(db)
    return jsonify({"status":"ok"})

@app.route("/choose_language")
def choose_language():
    if "user" not in session: return redirect(url_for("login"))
    next_page = request.args.get("next", "/topic/Language")
    return render_template("choose_language.html", username=session["user"], next_page=next_page)

@app.route("/set_language", methods=["POST"])
def set_language():
    if "user" not in session: return jsonify({"error":"not logged in"})
    data = request.get_json()
    language = data.get("language", "Malay")
    db = load_db()
    db["users"][session["user"]]["chosen_language"] = language
    save_db(db)
    session["chosen_language"] = language
    return jsonify({"status":"ok"})

@app.route("/topic/<name>")
def topic(name):
    if "user" not in session: return redirect(url_for("login"))
    if name not in TOPIC_META: return redirect(url_for("home"))
    # If Language topic and no language chosen yet, redirect to choose
    if name == "Language" and "chosen_language" not in session:
        return redirect(url_for("choose_language", next="/topic/Language"))
    db   = load_db()
    user = db["users"].get(session["user"],{})
    diff = user.get("difficulty",{}).get(name,"Beginner")
    buddy_key  = user.get("buddy","Cosmo")
    buddy_data = BUDDIES.get(buddy_key, BUDDIES["Cosmo"])
    return render_template("topic.html", topic=name, meta=TOPIC_META[name],
                           difficulty=diff, username=session["user"],
                           buddy=buddy_key, buddy_data=buddy_data)

@app.route("/flashcards/<topic_name>")
def flashcards(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    # Level-based flashcard data - each level teaches NEW content
    level = request.args.get("level", None)
    db = load_db()
    user = db["users"].get(session["user"],{})
    if not level:
        level = user.get("difficulty",{}).get(topic_name,"Beginner")
    
    FLASHCARD_DATA = {
        "Animals": {
            "Beginner": [
                {"word":"Dog","fact":"Dogs are loyal pets that wag their tails when happy!","image":"https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=200&h=200&fit=crop"},
                {"word":"Cat","fact":"Cats purr when happy and can see in the dark!","image":"https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=200&h=200&fit=crop"},
                {"word":"Rabbit","fact":"Rabbits have long ears and love to hop around!","image":"https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=200&h=200&fit=crop"},
                {"word":"Fish","fact":"Fish live in water and breathe through gills!","image":"https://images.unsplash.com/photo-1524704654690-b56c05c78a00?w=200&h=200&fit=crop"},
                {"word":"Bird","fact":"Birds have feathers and most can fly!","image":"https://images.unsplash.com/photo-1444464666168-49d633b86797?w=200&h=200&fit=crop"},
            ],
            "Intermediate": [
                {"word":"Elephant","fact":"Elephants are the largest land animals and never forget!","image":"https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=200&h=200&fit=crop"},
                {"word":"Lion","fact":"Lions live in groups called prides. Males have big manes!","image":"https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=200&h=200&fit=crop"},
                {"word":"Penguin","fact":"Penguins are birds that swim instead of fly!","image":"https://images.unsplash.com/photo-1551986782-d0169b3f8fa7?w=200&h=200&fit=crop"},
                {"word":"Giraffe","fact":"Giraffes have the longest necks of any animal!","image":"https://images.unsplash.com/photo-1547721064-da6cfb341d50?w=200&h=200&fit=crop"},
                {"word":"Dolphin","fact":"Dolphins are very smart and talk with clicks!","image":"https://images.unsplash.com/photo-1607153333879-c174d265f1d2?w=200&h=200&fit=crop"},
            ],
            "Advanced": [
                {"word":"Cheetah","fact":"Cheetahs are the fastest land animals at 70 mph!","image":"https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=200&h=200&fit=crop"},
                {"word":"Chameleon","fact":"Chameleons can change colour to hide from predators!","image":"https://images.unsplash.com/photo-1504450874802-0ba2bcd659e0?w=200&h=200&fit=crop"},
                {"word":"Octopus","fact":"Octopuses have 8 arms and 3 hearts!","image":"https://images.unsplash.com/photo-1545671913-b89ac1b4ac10?w=200&h=200&fit=crop"},
                {"word":"Kangaroo","fact":"Baby kangaroos are called joeys and live in pouches!","image":"https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=200&h=200&fit=crop"},
                {"word":"Eagle","fact":"Eagles can see 8 times better than humans!","image":"https://images.unsplash.com/photo-1611689342806-0863700ce8e4?w=200&h=200&fit=crop"},
            ],
        },
        "Colours": {
            "Beginner": [
                {"word":"Red","fact":"Red is the colour of strawberries and fire trucks!","image":"https://images.unsplash.com/photo-1490750967868-88aa4f1a4f0a?w=200&h=200&fit=crop"},
                {"word":"Blue","fact":"Blue is the colour of the sky and the ocean!","image":"https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=200&h=200&fit=crop"},
                {"word":"Yellow","fact":"Yellow is the colour of the sun and bananas!","image":"https://images.unsplash.com/photo-1557800636-894a64c1696f?w=200&h=200&fit=crop"},
                {"word":"Green","fact":"Green is the colour of grass, trees, and frogs!","image":"https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=200&h=200&fit=crop"},
                {"word":"Orange","fact":"Orange is the colour of pumpkins and carrots!","image":"https://images.unsplash.com/photo-1547514701-42782101795e?w=200&h=200&fit=crop"},
            ],
            "Intermediate": [
                {"word":"Purple","fact":"Purple is made by mixing red and blue together!","image":"https://images.unsplash.com/photo-1490750967868-88aa4f1a4f0a?w=200&h=200&fit=crop"},
                {"word":"Pink","fact":"Pink is a lighter version of red. Flamingos are pink!","image":"https://images.unsplash.com/photo-1490750967868-88aa4f1a4f0a?w=200&h=200&fit=crop"},
                {"word":"Brown","fact":"Brown is the colour of chocolate and tree trunks!","image":"https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=200&h=200&fit=crop"},
                {"word":"Black","fact":"Black is the colour of night. Mix all colours to get it!","image":"https://images.unsplash.com/photo-1519681393784-d120267933ba?w=200&h=200&fit=crop"},
                {"word":"White","fact":"White is the colour of snow and clouds!","image":"https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=200&h=200&fit=crop"},
            ],
            "Advanced": [
                {"word":"Primary Colours","fact":"Red, blue, and yellow cannot be made by mixing!","image":"https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=200&h=200&fit=crop"},
                {"word":"Secondary Colours","fact":"Green, orange, purple are made by mixing primaries!","image":"https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=200&h=200&fit=crop"},
                {"word":"Warm Colours","fact":"Red, orange, yellow feel warm like fire and sun!","image":"https://images.unsplash.com/photo-1490750967868-88aa4f1a4f0a?w=200&h=200&fit=crop"},
                {"word":"Cool Colours","fact":"Blue, green, purple feel cool like water and ice!","image":"https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=200&h=200&fit=crop"},
                {"word":"Rainbow","fact":"Rainbows have 7 colours: red, orange, yellow, green, blue, indigo, violet!","image":"https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=200&h=200&fit=crop"},
            ],
        },
        "Shapes": {
            "Beginner": [
                {"word":"Circle","fact":"A circle is perfectly round with no corners!","image":"SVG_CIRCLE"},
                {"word":"Square","fact":"A square has 4 equal sides and 4 corners!","image":"SVG_SQUARE"},
                {"word":"Triangle","fact":"A triangle has 3 sides and 3 corners!","image":"SVG_TRIANGLE"},
            ],
            "Intermediate": [
                {"word":"Rectangle","fact":"A rectangle has 2 long sides and 2 short sides!","image":"SVG_RECTANGLE"},
                {"word":"Star","fact":"A star shape has 5 points sticking out!","image":"SVG_STAR"},
                {"word":"Oval","fact":"An oval is like a stretched circle, like an egg!","image":"SVG_CIRCLE"},
                {"word":"Pentagon","fact":"A pentagon has 5 sides. Penta means five!","image":"SVG_STAR"},
            ],
            "Advanced": [
                {"word":"Hexagon","fact":"A hexagon has 6 sides. Honeycombs are hexagons!","image":"SVG_STAR"},
                {"word":"Octagon","fact":"An octagon has 8 sides. Stop signs are octagons!","image":"SVG_STAR"},
                {"word":"Cube","fact":"A cube is a 3D square. Dice are cubes!","image":"SVG_SQUARE"},
                {"word":"Sphere","fact":"A sphere is a 3D circle. Balls are spheres!","image":"SVG_CIRCLE"},
                {"word":"Cylinder","fact":"A cylinder is like a can. It has 2 circles and a tube!","image":"SVG_RECTANGLE"},
            ],
        },
        "Numbers": {
            "Beginner": [
                {"word":"One","fact":"One is the first number. You have one nose!","image":"SVG_ONE"},
                {"word":"Two","fact":"Two is the number of your eyes and ears!","image":"SVG_TWO"},
                {"word":"Five","fact":"Five is the number of fingers on one hand!","image":"SVG_FIVE"},
                {"word":"Ten","fact":"Ten is the number of all your fingers together!","image":"SVG_TEN"},
            ],
            "Intermediate": [
                {"word":"Addition","fact":"Adding means putting numbers together. 2+3=5!","image":"SVG_FIVE"},
                {"word":"Subtraction","fact":"Subtracting means taking away. 5-2=3!","image":"SVG_TWO"},
                {"word":"Twenty","fact":"Twenty is 2 groups of ten. 10+10=20!","image":"SVG_TEN"},
                {"word":"Dozen","fact":"A dozen means 12. A dozen eggs has 12 eggs!","image":"SVG_TEN"},
            ],
            "Advanced": [
                {"word":"Multiplication","fact":"Multiplying is fast adding. 3x4 means 3+3+3+3=12!","image":"SVG_TEN"},
                {"word":"Division","fact":"Dividing means sharing equally. 10 divided by 2 is 5!","image":"SVG_FIVE"},
                {"word":"Hundred","fact":"One hundred is 10 groups of 10. Written as 100!","image":"SVG_TEN"},
                {"word":"Fractions","fact":"A fraction is part of a whole. Half means 1 out of 2!","image":"SVG_TWO"},
                {"word":"Even and Odd","fact":"Even numbers split in 2 (2,4,6). Odd numbers don't (1,3,5)!","image":"SVG_FIVE"},
            ],
        },
        "Language": {
            "Beginner": [
                {"word":"Hello","fact":"Hello is how we greet people! In Spanish it is Hola!","image":"https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=200&h=200&fit=crop"},
                {"word":"Please","fact":"Please is a magic word that shows good manners!","image":"https://images.unsplash.com/photo-1531206715517-5c0ba140b2b8?w=200&h=200&fit=crop"},
                {"word":"Thank You","fact":"Thank you shows someone you are grateful!","image":"https://images.unsplash.com/photo-1521791136064-7986c2920216?w=200&h=200&fit=crop"},
                {"word":"Sorry","fact":"Sorry is what we say when we make a mistake!","image":"https://images.unsplash.com/photo-1516585427167-9f4af9627e6c?w=200&h=200&fit=crop"},
            ],
            "Intermediate": [
                {"word":"Alphabet","fact":"The alphabet has 26 letters from A to Z!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
                {"word":"Vowels","fact":"A, E, I, O, U are vowels. Every word needs one!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
                {"word":"Sentence","fact":"A sentence starts with a capital and ends with a full stop!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
                {"word":"Rhyming","fact":"Rhyming words sound the same at the end. Cat, hat, bat!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
            ],
            "Advanced": [
                {"word":"Noun","fact":"A noun is a person, place, or thing. Dog, school, book!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
                {"word":"Verb","fact":"A verb is an action word. Run, jump, eat, sleep!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
                {"word":"Adjective","fact":"An adjective describes things. Big, small, happy, red!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
                {"word":"Synonym","fact":"Synonyms mean the same thing. Happy and glad are synonyms!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
                {"word":"Antonym","fact":"Antonyms are opposites. Hot and cold are antonyms!","image":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=200&fit=crop"},
            ],
        },
    }
    topic_data = FLASHCARD_DATA.get(topic_name, FLASHCARD_DATA["Animals"])
    cards = topic_data.get(level, topic_data.get("Beginner",[]))
    meta = TOPIC_META.get(topic_name, {})
    return render_template("flashcards.html", topic=topic_name, cards=cards, meta=meta, 
                           username=session["user"], level=level)

@app.route("/story/<topic_name>")
def story(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    stories = {
        "Animals": [
            "Once upon a time, in a sunny savanna, a little lion cub named Leo woke up.",
            "Leo stretched and roared a tiny roar. His friends heard him and came running!",
            "Ellie the Elephant sprayed water playfully. Good morning Leo! she said.",
            "Gigi the Giraffe bent her long neck down. Want to play? she asked.",
            "Penny the Penguin waddled over. Can I join too? she asked shyly.",
            "They all played together until the sun set. Leo learned that friends come in all shapes and sizes!",
        ],
        "Colours": [
            "In a magical land, everything was grey and boring.",
            "One day, a rainbow appeared and painted the sky with beautiful colours!",
            "Red painted the roses, blue painted the ocean, and yellow painted the sun!",
            "Green covered the grass, and purple decorated the flowers!",
            "Orange painted the sunset, and pink coloured the flamingos!",
            "The world was now full of colour, and everyone was happy! The end!",
        ],
        "Shapes": [
            "In Shape Town, all the shapes lived together happily.",
            "Circle loved to roll around the park. She was perfectly round with no corners!",
            "Triangle was strong and pointy. He had three sides and three corners.",
            "Square was very neat and tidy. All four of his sides were exactly the same!",
            "Rectangle was tall and proud. She had two long sides and two short sides.",
            "Together they built a beautiful house. Every shape is special and important!",
        ],
        "Numbers": [
            "In Number Land, the numbers loved to play counting games.",
            "One was always first. I am number one! he said proudly.",
            "Two loved pairs. I have two eyes, two ears, and two hands! she said.",
            "Five was very helpful. High five! he said, showing all five fingers.",
            "Ten was the biggest. I am all your fingers together! she laughed.",
            "Zero was special too. Without me, you cannot make ten or one hundred! The numbers all cheered!",
        ],
        "Language": [
            "In Word Village, the words helped people talk to each other.",
            "Hello was always the first to greet everyone. Hi there! she waved.",
            "Please was very polite. May I have some water, please? he asked kindly.",
            "Thank You was grateful. Thank you for helping me! she smiled.",
            "Sorry was brave. I am sorry I bumped into you, he said honestly.",
            "Together, the words made the world a kinder, friendlier place! The end!",
        ],
    }
    pages = stories.get(topic_name, None)
    if pages is None:
        return redirect(url_for("topic", name=topic_name))
    meta = TOPIC_META.get(topic_name, {})
    return render_template("story.html", topic=topic_name, pages=pages, meta=meta, username=session["user"])

@app.route("/quiz/<topic_name>")
def quiz(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    db   = load_db()
    user = db["users"].get(session["user"],{})
    diff = request.args.get("diff") or user.get("difficulty",{}).get(topic_name,"Beginner")
    questions = QUIZ.get(topic_name,{}).get(diff,[])
    if not questions: questions = QUIZ.get(topic_name,{}).get("Beginner",[])
    buddy_key  = user.get("buddy","Cosmo")
    buddy_data = BUDDIES.get(buddy_key, BUDDIES["Cosmo"])
    hints  = BUDDY_HINTS.get(buddy_key, BUDDY_HINTS["Cosmo"])
    praise = BUDDY_PRAISE.get(buddy_key, BUDDY_PRAISE["Cosmo"])
    return render_template("quiz.html", topic=topic_name,
                           questions=questions, meta=TOPIC_META.get(topic_name,{}),
                           difficulty=diff, username=session["user"],
                           buddy=buddy_key, buddy_data=buddy_data,
                           hints=hints, praise=praise)

@app.route("/quiz_result", methods=["POST"])
def quiz_result():
    if "user" not in session: return jsonify({"error":"not logged in"})
    data  = request.get_json()
    topic_name = data.get("topic","Animals")
    score = data.get("score",0)
    total = data.get("total",0)
    diff  = data.get("difficulty","Beginner")
    pct   = int(score/total*100) if total else 0
    db    = load_db()
    user  = session["user"]
    db["users"][user].setdefault("sessions",[]).append({
        "topic":topic_name,"score":score,"total":total,
        "percent":pct,"difficulty":diff,
        "date":datetime.now().strftime("%Y-%m-%d %H:%M"),"type":"quiz"
    })
    if topic_name not in db["users"][user].get("topics_tried",[]):
        db["users"][user].setdefault("topics_tried",[]).append(topic_name)
    save_db(db)
    return jsonify({"status":"ok","percent":pct})

@app.route("/chat")
def chat():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("chat.html", username=session["user"])

@app.route("/badges")
def badges():
    if "user" not in session: return redirect(url_for("login"))
    db = load_db()
    user = db["users"].get(session["user"],{})
    earned = set(user.get("badges",[]))
    sessions = user.get("sessions",[])
    ALL_BADGES = [
        {"id":"first_quiz","icon":"🎯","name":"First Quiz","desc":"Complete your first quiz","earned":"first_quiz" in earned},
        {"id":"perfect","icon":"💯","name":"Perfect Score","desc":"Get 100% on a quiz","earned":"perfect" in earned},
        {"id":"streak3","icon":"🔥","name":"On Fire","desc":"3 sessions in a row","earned":"streak3" in earned},
        {"id":"all_topics","icon":"🌟","name":"Explorer","desc":"Try all 5 topics","earned":"all_topics" in earned},
        {"id":"speed","icon":"⚡","name":"Speed Star","desc":"Finish a quiz in under 30s","earned":"speed" in earned},
        {"id":"minigame","icon":"🎮","name":"Game Master","desc":"Play a mini-game","earned":"minigame" in earned},
        {"id":"helper","icon":"💬","name":"Curious Mind","desc":"Ask Sparky 5 questions","earned":"helper" in earned},
        {"id":"reader","icon":"📖","name":"Story Lover","desc":"Read 3 stories","earned":"reader" in earned},
        {"id":"cards","icon":"🃏","name":"Card Collector","desc":"View all flashcards","earned":"cards" in earned},
        {"id":"level5","icon":"👑","name":"Level 5","desc":"Reach level 5","earned":"level5" in earned},
        {"id":"combo","icon":"🎯","name":"Combo King","desc":"Get a x5 combo in mini-game","earned":"combo" in earned},
        {"id":"daily","icon":"📅","name":"Daily Learner","desc":"Learn 5 days in a row","earned":"daily" in earned},
    ]
    earned_count = sum(1 for b in ALL_BADGES if b["earned"])
    streak = min(len(sessions), 7)
    return render_template("badges.html", username=session["user"],
                           all_badges=ALL_BADGES, earned_count=earned_count,
                           total_badges=len(ALL_BADGES), streak=streak)

@app.route("/progress")
def progress():
    if "user" not in session: return redirect(url_for("login"))
    db = load_db()
    user = db["users"].get(session["user"],{})
    sessions = user.get("sessions",[])
    # Calculate level and XP
    total_xp = sum(s.get("score",0)*10 for s in sessions)
    level = total_xp // 100 + 1
    xp = total_xp % 100
    xp_next = 100
    # Topic progress
    topic_scores = {}
    topic_times = {}
    for s in sessions:
        t = s.get("topic","")
        topic_scores.setdefault(t,[]).append(s.get("percent",0))
        topic_times.setdefault(t,[]).append(s.get("time_taken",0))
    colors = {"Animals":"#FF9F43","Colours":"#AB47BC","Shapes":"#42A5F5","Numbers":"#43A047","Language":"#FF7043"}
    topic_progress = []
    for t in ["Animals","Colours","Shapes","Numbers","Language"]:
        scores = topic_scores.get(t,[])
        times = topic_times.get(t,[])
        pct = int(sum(scores)/len(scores)) if scores else 0
        avg_time = int(sum(times)/len(times)) if times else 0
        diff = user.get("difficulty",{}).get(t,"Beginner")
        topic_progress.append({"name":t,"pct":pct,"color":colors.get(t,"#888"),"avg_time":avg_time,"level":diff})
    # Mood history
    mood_history = user.get("mood_history",[])
    current_mood = user.get("mood","happy")
    # Areas to improve (topics below 60%)
    needs_improvement = [t for t in topic_progress if 0 < t["pct"] < 60]
    # Recent
    recent = []
    for s in sessions[-5:][::-1]:
        recent.append({"topic":s.get("topic",""),"date":s.get("date",""),"score":s.get("score",0),
                       "total":s.get("total",0),"time_taken":s.get("time_taken",0)})
    # Badges
    badges = user.get("badges",[])
    return render_template("progress.html", username=session["user"],
                           level=level, xp=xp, xp_next=xp_next, xp_pct=min(xp,100),
                           topic_progress=topic_progress, recent=recent,
                           current_mood=current_mood, needs_improvement=needs_improvement,
                           badges=badges, role=user.get("role","child"))

@app.route("/generate_content", methods=["POST"])
def generate_content():
    """Generate learning content dynamically using Bedrock and redirect to lesson page"""
    if "user" not in session: return jsonify({"error":"not logged in"})
    data = request.get_json()
    topic = data.get("topic","")
    mode = data.get("mode","flashcards")
    
    import boto3, json as j
    
    # Store topic in session
    session["current_topic"] = topic
    session["current_mode"] = mode
    
    if mode == "flashcards":
        # Generate flashcard data
        prompt = f"Create exactly 5 flashcards about '{topic}' for a child aged 5-10. Return ONLY a JSON array like this: [{{'word':'concept','fact':'one fun fact sentence'}}]. No other text, just the JSON array."
        try:
            client = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
            body = j.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":500,"messages":[{"role":"user","content":prompt}],"system":"Return only valid JSON. No markdown, no explanation."})
            response = client.invoke_model(modelId='anthropic.claude-3-haiku-20240307-v1:0', body=body, contentType='application/json')
            text = j.loads(response['body'].read())['content'][0]['text']
            # Try to parse JSON from response
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                cards = j.loads(match.group())
            else:
                cards = [{"word":topic,"fact":f"This is about {topic}!"}]
        except:
            cards = [
                {"word":topic.title(),"fact":f"{topic.title()} is a fascinating subject to learn about!"},
                {"word":"Fun Fact","fact":f"There are many interesting things about {topic}!"},
                {"word":"Did You Know","fact":f"Learning about {topic} makes you smarter every day!"},
                {"word":"Amazing","fact":f"{topic.title()} is all around us in the world!"},
                {"word":"Keep Learning","fact":f"The more you learn about {topic}, the more you discover!"},
            ]
        # Add images
        for c in cards:
            c.setdefault("image", f"https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=200&h=200&fit=crop")
        session["generated_cards"] = cards
        session.modified = True
        return jsonify({"redirect":"/lesson/flashcards"})
    
    elif mode == "quiz":
        prompt = f"Create 4 quiz questions about '{topic}' for a child aged 5-10. Return ONLY a JSON array like: [{{'q':'question text','choices':['A','B','C','D'],'a':'correct answer'}}]. No other text."
        try:
            client = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
            body = j.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":500,"messages":[{"role":"user","content":prompt}],"system":"Return only valid JSON. No markdown."})
            response = client.invoke_model(modelId='anthropic.claude-3-haiku-20240307-v1:0', body=body, contentType='application/json')
            text = j.loads(response['body'].read())['content'][0]['text']
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                questions = j.loads(match.group())
            else:
                questions = [{"q":f"What is {topic}?","choices":["Fun","Boring","Scary","Hard"],"a":"Fun"}]
        except:
            questions = [
                {"q":f"Is {topic} fun to learn?","choices":["Yes!","No","Maybe","Never"],"a":"Yes!"},
                {"q":f"Can you learn about {topic} every day?","choices":["Yes!","No","Only Mondays","Only at school"],"a":"Yes!"},
                {"q":f"What helps you learn {topic}?","choices":["Practice","Sleeping","Ignoring it","Running away"],"a":"Practice"},
                {"q":f"Who can learn about {topic}?","choices":["Everyone!","Only adults","Only teachers","Nobody"],"a":"Everyone!"},
            ]
        session["generated_quiz"] = questions
        session.modified = True
        return jsonify({"redirect":"/lesson/quiz"})
    
    elif mode == "stories":
        prompt = f"Write a short educational story about '{topic}' for a child aged 5-10. Make it 4 short paragraphs (2-3 sentences each). Simple words. Fun and educational."
        try:
            client = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
            body = j.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":600,"messages":[{"role":"user","content":prompt}],"system":"Write a simple children's story. Use short sentences."})
            response = client.invoke_model(modelId='anthropic.claude-3-haiku-20240307-v1:0', body=body, contentType='application/json')
            story = j.loads(response['body'].read())['content'][0]['text']
        except:
            story = f"Once upon a time, there was a curious child who wanted to learn about {topic}.\n\nThey discovered that {topic} is amazing and full of surprises!\n\nEvery day they learned something new and exciting about {topic}.\n\nThe end! Keep being curious and never stop learning!"
        session["generated_story"] = story
        session.modified = True
        return jsonify({"redirect":"/lesson/story"})
    
    else:  # game
        prompt = f"Create 8 quiz questions about '{topic}' for a child aged 5-10. Return ONLY a JSON array like: [{{'q':'question text','choices':['A','B','C','D'],'a':'correct answer'}}]. No other text."
        try:
            client = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
            body = j.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":600,"messages":[{"role":"user","content":prompt}],"system":"Return only valid JSON. No markdown."})
            response = client.invoke_model(modelId='anthropic.claude-3-haiku-20240307-v1:0', body=body, contentType='application/json')
            text = j.loads(response['body'].read())['content'][0]['text']
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                questions = j.loads(match.group())
            else:
                questions = [{"q":f"What is 2+2?","choices":["3","4","5","6"],"a":"4"}]
        except:
            questions = [
                {"q":"What is 3 + 4?","choices":["5","6","7","8"],"a":"7"},
                {"q":"What is 5 x 2?","choices":["8","10","12","15"],"a":"10"},
                {"q":"What is 9 - 3?","choices":["4","5","6","7"],"a":"6"},
                {"q":"What is 6 + 6?","choices":["10","11","12","13"],"a":"12"},
                {"q":"What is 4 x 3?","choices":["10","11","12","14"],"a":"12"},
                {"q":"What is 15 - 7?","choices":["6","7","8","9"],"a":"8"},
                {"q":"What is 2 + 9?","choices":["10","11","12","13"],"a":"11"},
                {"q":"What is 8 x 2?","choices":["14","15","16","18"],"a":"16"},
            ]
        session["generated_game_questions"] = questions
        session.modified = True
        return jsonify({"redirect":"/lesson/game"})

@app.route("/lesson/game")
def lesson_game():
    if "user" not in session: return redirect(url_for("login"))
    questions = session.get("generated_game_questions",[])
    topic = session.get("current_topic","Learning")
    return render_template("lesson_game.html", questions=questions, topic=topic, username=session["user"])

@app.route("/lesson/flashcards")
def lesson_flashcards():
    if "user" not in session: return redirect(url_for("login"))
    cards = session.get("generated_cards",[])
    topic = session.get("current_topic","Learning")
    return render_template("lesson_flashcards.html", cards=cards, topic=topic, username=session["user"])

@app.route("/lesson/quiz")
def lesson_quiz():
    if "user" not in session: return redirect(url_for("login"))
    questions = session.get("generated_quiz",[])
    topic = session.get("current_topic","Learning")
    return render_template("lesson_quiz.html", questions=questions, topic=topic, username=session["user"])

@app.route("/lesson/story")
def lesson_story():
    if "user" not in session: return redirect(url_for("login"))
    story = session.get("generated_story","")
    topic = session.get("current_topic","Learning")
    return render_template("lesson_story.html", story=story, topic=topic, username=session["user"])

@app.route("/minigame/<topic_name>")
def minigame(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    return redirect(url_for("games", topic_name=topic_name))

@app.route("/games/<topic_name>")
def games(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    return render_template("games.html", topic=topic_name, username=session["user"])

@app.route("/speedgame/<topic_name>")
def speedgame(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    questions = QUIZ.get(topic_name,{}).get("Beginner",[])
    return render_template("speedgame.html", topic=topic_name, questions=questions, username=session["user"])

@app.route("/sortgame/<topic_name>")
def sortgame(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    return render_template("sortgame.html", topic=topic_name, username=session["user"])

@app.route("/minigame_actual/<topic_name>")
def minigame_actual(topic_name):
    if "user" not in session: return redirect(url_for("login"))
    # Matching pairs per topic
    GAME_PAIRS = {
        "Animals": [
            {"left":"🐶","leftLabel":"Dog","right":"Woof!","rightLabel":"Sound"},
            {"left":"🐱","leftLabel":"Cat","right":"Meow!","rightLabel":"Sound"},
            {"left":"🐮","leftLabel":"Cow","right":"Moo!","rightLabel":"Sound"},
            {"left":"🦁","leftLabel":"Lion","right":"Roar!","rightLabel":"Sound"},
            {"left":"🐸","leftLabel":"Frog","right":"Ribbit!","rightLabel":"Sound"},
            {"left":"🐦","leftLabel":"Bird","right":"Tweet!","rightLabel":"Sound"},
        ],
        "Colours": [
            {"left":"🔴","leftLabel":"Red","right":"Strawberry","rightLabel":"Example"},
            {"left":"🔵","leftLabel":"Blue","right":"Ocean","rightLabel":"Example"},
            {"left":"🟡","leftLabel":"Yellow","right":"Banana","rightLabel":"Example"},
            {"left":"🟢","leftLabel":"Green","right":"Grass","rightLabel":"Example"},
            {"left":"🟠","leftLabel":"Orange","right":"Carrot","rightLabel":"Example"},
            {"left":"🟣","leftLabel":"Purple","right":"Grape","rightLabel":"Example"},
        ],
        "Shapes": [
            {"left":"▲","leftLabel":"Triangle","right":"3 sides","rightLabel":"Sides"},
            {"left":"■","leftLabel":"Square","right":"4 equal sides","rightLabel":"Sides"},
            {"left":"●","leftLabel":"Circle","right":"0 corners","rightLabel":"Corners"},
            {"left":"▬","leftLabel":"Rectangle","right":"2 long + 2 short","rightLabel":"Sides"},
            {"left":"★","leftLabel":"Star","right":"5 points","rightLabel":"Points"},
            {"left":"⬡","leftLabel":"Hexagon","right":"6 sides","rightLabel":"Sides"},
        ],
        "Numbers": [
            {"left":"1+1","leftLabel":"Addition","right":"2","rightLabel":"Answer"},
            {"left":"2+2","leftLabel":"Addition","right":"4","rightLabel":"Answer"},
            {"left":"3+2","leftLabel":"Addition","right":"5","rightLabel":"Answer"},
            {"left":"5-2","leftLabel":"Subtraction","right":"3","rightLabel":"Answer"},
            {"left":"4+4","leftLabel":"Addition","right":"8","rightLabel":"Answer"},
            {"left":"10-3","leftLabel":"Subtraction","right":"7","rightLabel":"Answer"},
        ],
        "Language": [
            {"left":"Hello","leftLabel":"English","right":"Hola","rightLabel":"Spanish"},
            {"left":"Thank you","leftLabel":"English","right":"Gracias","rightLabel":"Spanish"},
            {"left":"Please","leftLabel":"English","right":"Por favor","rightLabel":"Spanish"},
            {"left":"Goodbye","leftLabel":"English","right":"Adios","rightLabel":"Spanish"},
            {"left":"Friend","leftLabel":"English","right":"Amigo","rightLabel":"Spanish"},
            {"left":"Love","leftLabel":"English","right":"Amor","rightLabel":"Spanish"},
        ],
    }
    pairs = GAME_PAIRS.get(topic_name, GAME_PAIRS["Animals"])
    return render_template("minigame.html", topic=topic_name, pairs=pairs, username=session["user"])

@app.route("/chat_message", methods=["POST"])
def chat_message():
    """Smart chatbot powered by Bedrock with conversation memory."""
    msg = request.get_json().get("message","").lower().strip()
    # Maintain conversation history in session
    if "chat_history" not in session:
        session["chat_history"] = []
    session["chat_history"].append({"role":"user","content":msg})
    # Keep last 20 messages for context
    if len(session["chat_history"]) > 20:
        session["chat_history"] = session["chat_history"][-20:]
    reply = get_reply(msg, session["chat_history"])
    session["chat_history"].append({"role":"assistant","content":reply})
    session.modified = True
    return jsonify({"reply": reply})

@app.route("/get_image")
def get_image():
    """Return a topic-relevant image URL"""
    q = request.args.get("q", "nature").lower()
    image_map = {
        # Shapes
        "circle":"https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=300&h=180&fit=crop",
        "triangle":"https://images.unsplash.com/photo-1494059980473-813e73ee784b?w=300&h=180&fit=crop",
        "square":"https://images.unsplash.com/photo-1518012312832-96aea3c91144?w=300&h=180&fit=crop",
        "rectangle":"https://images.unsplash.com/photo-1518012312832-96aea3c91144?w=300&h=180&fit=crop",
        "shapes":"https://images.unsplash.com/photo-1509228468518-180dd4864904?w=300&h=180&fit=crop",
        # Numbers
        "counting":"https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=300&h=180&fit=crop",
        "numbers":"https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=300&h=180&fit=crop",
        "math":"https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=300&h=180&fit=crop",
        # Colours
        "rainbow":"https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=300&h=180&fit=crop",
        "red apple":"https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=300&h=180&fit=crop",
        "blue sky":"https://images.unsplash.com/photo-1517483000871-1dbf64a6e1c6?w=300&h=180&fit=crop",
        "sunflower":"https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=300&h=180&fit=crop",
        # Nature
        "plant":"https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=300&h=180&fit=crop",
        "flower":"https://images.unsplash.com/photo-1490750967868-88aa4f1a4f0a?w=300&h=180&fit=crop",
        "tree":"https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=300&h=180&fit=crop",
        "ocean":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300&h=180&fit=crop",
        "sea":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300&h=180&fit=crop",
        "forest":"https://images.unsplash.com/photo-1448375240586-882707db888b?w=300&h=180&fit=crop",
        # Animals
        "fish":"https://images.unsplash.com/photo-1524704654690-b56c05c78a00?w=300&h=180&fit=crop",
        "dog":"https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=300&h=180&fit=crop",
        "cat":"https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=300&h=180&fit=crop",
        "lion":"https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=300&h=180&fit=crop",
        "elephant":"https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=300&h=180&fit=crop",
        "bird":"https://images.unsplash.com/photo-1444464666168-49d633b86797?w=300&h=180&fit=crop",
        "dolphin":"https://images.unsplash.com/photo-1607153333879-c174d265f1d2?w=300&h=180&fit=crop",
        "shark":"https://images.unsplash.com/photo-1560275619-4662e36fa65c?w=300&h=180&fit=crop",
        "butterfly":"https://images.unsplash.com/photo-1452570053594-1b985d6ea890?w=300&h=180&fit=crop",
        "frog":"https://images.unsplash.com/photo-1474511320723-9a56873571b7?w=300&h=180&fit=crop",
        "rabbit":"https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=300&h=180&fit=crop",
        "horse":"https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=300&h=180&fit=crop",
        "monkey":"https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?w=300&h=180&fit=crop",
        "bear":"https://images.unsplash.com/photo-1525382455947-f319bc05fb35?w=300&h=180&fit=crop",
        "penguin":"https://images.unsplash.com/photo-1551986782-d0169b3f8fa7?w=300&h=180&fit=crop",
        "giraffe":"https://images.unsplash.com/photo-1547721064-da6cfb341d50?w=300&h=180&fit=crop",
        "snake":"https://images.unsplash.com/photo-1531386151447-fd76ad50012f?w=300&h=180&fit=crop",
        "bee":"https://images.unsplash.com/photo-1558642452-9d2a7deb7f62?w=300&h=180&fit=crop",
        # Space/Science
        "space":"https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=300&h=180&fit=crop",
        "planet":"https://images.unsplash.com/photo-1614732414444-096e5f1122d5?w=300&h=180&fit=crop",
        "sun":"https://images.unsplash.com/photo-1532693322450-2cb5c511067d?w=300&h=180&fit=crop",
        "moon":"https://images.unsplash.com/photo-1532693322450-2cb5c511067d?w=300&h=180&fit=crop",
        "star":"https://images.unsplash.com/photo-1519681393784-d120267933ba?w=300&h=180&fit=crop",
        "rain":"https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?w=300&h=180&fit=crop",
        "snow":"https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=300&h=180&fit=crop",
        # Objects
        "car":"https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=300&h=180&fit=crop",
        "food":"https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=300&h=180&fit=crop",
        "fruit":"https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=300&h=180&fit=crop",
        "robot":"https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=300&h=180&fit=crop",
        "book":"https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300&h=180&fit=crop",
        "music":"https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300&h=180&fit=crop",
        "ball":"https://images.unsplash.com/photo-1461896836934-bd45ba688b23?w=300&h=180&fit=crop",
        "sky":"https://images.unsplash.com/photo-1517483000871-1dbf64a6e1c6?w=300&h=180&fit=crop",
        "cloud":"https://images.unsplash.com/photo-1517483000871-1dbf64a6e1c6?w=300&h=180&fit=crop",
        "water":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300&h=180&fit=crop",
        "mountain":"https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=300&h=180&fit=crop",
        "farm":"https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=300&h=180&fit=crop",
        "house":"https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=300&h=180&fit=crop",
        "school":"https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=300&h=180&fit=crop",
    }
    for key, url in image_map.items():
        if key in q or q in key:
            return jsonify({"url": url})
    return jsonify({"url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=300&h=180&fit=crop"})

def get_reply(msg, history=None):
    """AI chatbot powered by Claude via Amazon Bedrock - generates structured lessons with memory"""
    import boto3, json as j
    try:
        client = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
        # Build messages with conversation history
        messages = []
        if history and len(history) > 1:
            # Include previous messages for context (skip the last one which is the current msg)
            for h in history[:-1]:
                messages.append({"role":h["role"],"content":h["content"]})
        messages.append({"role":"user","content":msg})
        body = j.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 600,
            "messages": messages,
            "system": """You are Thinkie, a friendly learning buddy for children aged 3-10 with special needs (autism, ADHD, cognitive delays).

RULES:
- Use simple words a 5-year-old understands
- Always be positive and encouraging
- Never be scary or negative
- Use short sentences (max 10 words each)
- STAY ON THE CURRENT TOPIC until the child asks to change
- Do NOT switch topics on your own
- Always include a relevant [Picture: keyword] for the topic being discussed

WHEN A CHILD WANTS TO LEARN SOMETHING, follow this EXACT format:

Let me teach you about [topic]!

[Picture: relevant keyword for the topic]

Fun Fact 1: [simple fact in one short sentence]

Fun Fact 2: [simple fact in one short sentence]

Fun Fact 3: [simple fact in one short sentence]

Great job learning about [topic]! I have games and quizzes ready for you on this topic. Would you like to:
- Try a quiz about [topic]?
- Play a game about [topic]?
- Learn more about [topic]?

IMPORTANT IMAGE RULES:
- For [Picture: X], use only 1-2 simple words that DIRECTLY relate to the topic
- For shapes: use [Picture: circle], [Picture: triangle], [Picture: square], [Picture: shapes]
- For numbers: use [Picture: counting], [Picture: numbers], [Picture: math]
- For colours: use [Picture: rainbow], [Picture: red apple], [Picture: blue sky]
- For animals: use the animal name like [Picture: lion], [Picture: elephant]
- ALWAYS include at least one [Picture:] in every response about a topic

STAYING ON TOPIC:
- If the child is learning about shapes, keep teaching shapes until they say otherwise
- If they say "more" or "next" or "continue", give more facts about the SAME topic
- Only change topic if they explicitly ask for a different topic
- After teaching, always remind them about available games and quizzes for that topic

WHEN THEY JUST ASK A SIMPLE QUESTION:
Answer in 1-2 short sentences with a relevant [Picture: keyword]. Add "Would you like to learn more about this?" at the end.

WHEN THEY SAY "quiz" or "test me":
Give ONE question at a time with a topic image:
[Picture: topic keyword]
Question: [simple question]?
A) [option]
B) [option]  
C) [option]
Tell me your answer!

WHEN THEY ANSWER a quiz:
If correct: "Amazing! You got it right!" then give next question with [Picture: keyword].
If wrong: "Good try! The answer is [answer]. Would you like to try another question?"

WHEN THEY SAY "game":
Say: "Great! Let me take you to the games!" and suggest they click on Games in the menu.
"""
        })
        response = client.invoke_model(modelId='anthropic.claude-3-haiku-20240307-v1:0', body=body, contentType='application/json')
        return j.loads(response['body'].read())['content'][0]['text']
    except Exception as e:
        return get_fallback_reply(msg)

def get_fallback_reply(msg):
    knowledge = {
        # Animals
        "lion": "Let me teach you about lions!\n\n[Picture: lion]\n\nFun Fact 1: Lions live in groups called prides.\n\nFun Fact 2: Male lions have a big fluffy mane.\n\nFun Fact 3: They are called the king of the jungle!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "elephant": "Let me teach you about elephants!\n\n[Picture: elephant]\n\nFun Fact 1: Elephants are the largest land animals.\n\nFun Fact 2: They have long trunks to grab food.\n\nFun Fact 3: Elephants never forget!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "dog": "Let me teach you about dogs!\n\n[Picture: dog]\n\nFun Fact 1: Dogs wag their tails when happy.\n\nFun Fact 2: They love to play fetch.\n\nFun Fact 3: Dogs are loyal friends!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "cat": "Let me teach you about cats!\n\n[Picture: cat]\n\nFun Fact 1: Cats purr when they are happy.\n\nFun Fact 2: They can see in the dark.\n\nFun Fact 3: Cats always land on their feet!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "fish": "Let me teach you about fish!\n\n[Picture: fish]\n\nFun Fact 1: Fish live in water and breathe through gills.\n\nFun Fact 2: They come in many beautiful colours.\n\nFun Fact 3: Some fish can even fly!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "rabbit": "Let me teach you about rabbits!\n\n[Picture: rabbit]\n\nFun Fact 1: Rabbits have long ears and fluffy tails.\n\nFun Fact 2: They love to hop around.\n\nFun Fact 3: Baby rabbits are called kittens!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "bird": "Let me teach you about birds!\n\n[Picture: bird]\n\nFun Fact 1: Birds have feathers and wings.\n\nFun Fact 2: Most birds can fly high in the sky.\n\nFun Fact 3: They sing beautiful songs in the morning!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "giraffe": "Let me teach you about giraffes!\n\n[Picture: giraffe]\n\nFun Fact 1: Giraffes have the longest necks.\n\nFun Fact 2: They eat leaves from tall trees.\n\nFun Fact 3: No two giraffes have the same spots!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "penguin": "Let me teach you about penguins!\n\n[Picture: penguin]\n\nFun Fact 1: Penguins are birds that cannot fly.\n\nFun Fact 2: They love to swim in cold water.\n\nFun Fact 3: They waddle when they walk!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "butterfly": "Let me teach you about butterflies!\n\n[Picture: butterfly]\n\nFun Fact 1: Butterflies start as caterpillars.\n\nFun Fact 2: They grow beautiful colourful wings.\n\nFun Fact 3: Butterflies drink nectar from flowers!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "dolphin": "Let me teach you about dolphins!\n\n[Picture: dolphin]\n\nFun Fact 1: Dolphins are very smart animals.\n\nFun Fact 2: They talk using clicks and whistles.\n\nFun Fact 3: Dolphins love to jump out of water!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "bear": "Let me teach you about bears!\n\n[Picture: bear]\n\nFun Fact 1: Bears are big and strong.\n\nFun Fact 2: Some bears sleep all winter long.\n\nFun Fact 3: Baby bears are called cubs!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "monkey": "Let me teach you about monkeys!\n\n[Picture: monkey]\n\nFun Fact 1: Monkeys are playful and clever.\n\nFun Fact 2: They swing from trees using their tails.\n\nFun Fact 3: Monkeys love bananas!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "shark": "Let me teach you about sharks!\n\n[Picture: shark]\n\nFun Fact 1: Sharks live in the ocean.\n\nFun Fact 2: They have lots of sharp teeth.\n\nFun Fact 3: Most sharks are not dangerous to people!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        "frog": "Let me teach you about frogs!\n\n[Picture: frog]\n\nFun Fact 1: Frogs start as tadpoles in water.\n\nFun Fact 2: They can jump very far.\n\nFun Fact 3: Some frogs are brightly coloured!\n\nGreat job! I have games and quizzes about animals ready for you. Would you like to try a quiz or play a game?",
        # Colours
        "red": "Let me teach you about the colour red!\n\n[Picture: red apple]\n\nFun Fact 1: Strawberries and fire trucks are red.\n\nFun Fact 2: Roses and ladybugs are red too.\n\nFun Fact 3: Red is a warm, bold colour!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "blue": "Let me teach you about the colour blue!\n\n[Picture: blue sky]\n\nFun Fact 1: The sky and ocean are blue.\n\nFun Fact 2: Blueberries are a yummy blue fruit.\n\nFun Fact 3: Blue is a cool, calm colour!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "yellow": "Let me teach you about the colour yellow!\n\n[Picture: sunflower]\n\nFun Fact 1: The sun and bananas are yellow.\n\nFun Fact 2: Sunflowers are bright yellow.\n\nFun Fact 3: Yellow is cheerful and happy!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "green": "Let me teach you about the colour green!\n\n[Picture: forest]\n\nFun Fact 1: Grass and leaves are green.\n\nFun Fact 2: Frogs and broccoli are green too.\n\nFun Fact 3: Green is the colour of nature!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "orange": "Let me teach you about the colour orange!\n\n[Picture: fruit]\n\nFun Fact 1: Oranges and carrots are orange.\n\nFun Fact 2: Pumpkins are orange too.\n\nFun Fact 3: Orange is warm and fun!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "purple": "Let me teach you about the colour purple!\n\n[Picture: flower]\n\nFun Fact 1: Grapes and plums are purple.\n\nFun Fact 2: Lavender flowers are purple.\n\nFun Fact 3: Purple is a royal colour!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "colour": "Let me teach you about colours!\n\n[Picture: rainbow]\n\nFun Fact 1: The primary colours are red, blue, and yellow.\n\nFun Fact 2: Mix them to make new colours.\n\nFun Fact 3: A rainbow has 7 beautiful colours!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "color": "Let me teach you about colours!\n\n[Picture: rainbow]\n\nFun Fact 1: The primary colours are red, blue, and yellow.\n\nFun Fact 2: Mix them to make new colours.\n\nFun Fact 3: A rainbow has 7 beautiful colours!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        "rainbow": "Let me teach you about rainbows!\n\n[Picture: rainbow]\n\nFun Fact 1: A rainbow has 7 colours.\n\nFun Fact 2: It appears after rain when the sun shines.\n\nFun Fact 3: The colours are red, orange, yellow, green, blue, indigo, violet!\n\nGreat job! I have games and quizzes about colours ready for you. Would you like to try a quiz or play a game?",
        # Shapes
        "circle": "Let me teach you about circles!\n\n[Picture: circle]\n\nFun Fact 1: A circle is perfectly round with no corners.\n\nFun Fact 2: Balls, coins, and wheels are circles.\n\nFun Fact 3: The sun looks like a big circle!\n\nGreat job! I have games and quizzes about shapes ready for you. Would you like to try a quiz or play a game?",
        "triangle": "Let me teach you about triangles!\n\n[Picture: triangle]\n\nFun Fact 1: A triangle has 3 sides and 3 corners.\n\nFun Fact 2: Pizza slices are shaped like triangles.\n\nFun Fact 3: Pyramids are made of triangles!\n\nGreat job! I have games and quizzes about shapes ready for you. Would you like to try a quiz or play a game?",
        "square": "Let me teach you about squares!\n\n[Picture: square]\n\nFun Fact 1: A square has 4 equal sides.\n\nFun Fact 2: Windows and tiles are often squares.\n\nFun Fact 3: A square has 4 corners!\n\nGreat job! I have games and quizzes about shapes ready for you. Would you like to try a quiz or play a game?",
        "rectangle": "Let me teach you about rectangles!\n\n[Picture: rectangle]\n\nFun Fact 1: A rectangle has 2 long and 2 short sides.\n\nFun Fact 2: Doors and books are rectangles.\n\nFun Fact 3: A rectangle has 4 corners!\n\nGreat job! I have games and quizzes about shapes ready for you. Would you like to try a quiz or play a game?",
        "shape": "Let me teach you about shapes!\n\n[Picture: shapes]\n\nFun Fact 1: Circles are round with no corners.\n\nFun Fact 2: Triangles have 3 sides.\n\nFun Fact 3: Squares have 4 equal sides!\n\nGreat job! I have games and quizzes about shapes ready for you. Would you like to try a quiz or play a game?",
        "star": "Let me teach you about stars!\n\n[Picture: star]\n\nFun Fact 1: A star shape has 5 points.\n\nFun Fact 2: You can see stars in the night sky.\n\nFun Fact 3: Stars are very far away and very bright!\n\nGreat job! I have games and quizzes about shapes ready for you. Would you like to try a quiz or play a game?",
        # Numbers
        "count": "Let me teach you to count!\n\n[Picture: counting]\n\nFun Fact 1: We count 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.\n\nFun Fact 2: You can count your fingers.\n\nFun Fact 3: Counting helps us know how many!\n\nGreat job! I have games and quizzes about numbers ready for you. Would you like to try a quiz or play a game?",
        "number": "Let me teach you about numbers!\n\n[Picture: numbers]\n\nFun Fact 1: Numbers help us count things.\n\nFun Fact 2: The first numbers are 1, 2, 3, 4, 5.\n\nFun Fact 3: We use numbers every day!\n\nGreat job! I have games and quizzes about numbers ready for you. Would you like to try a quiz or play a game?",
        "add": "Let me teach you about adding!\n\n[Picture: math]\n\nFun Fact 1: Adding means putting numbers together.\n\nFun Fact 2: 1 plus 1 equals 2.\n\nFun Fact 3: 2 plus 2 equals 4!\n\nGreat job! I have games and quizzes about numbers ready for you. Would you like to try a quiz or play a game?",
        "subtract": "Let me teach you about subtracting!\n\n[Picture: math]\n\nFun Fact 1: Subtracting means taking away.\n\nFun Fact 2: 5 minus 2 equals 3.\n\nFun Fact 3: 10 minus 5 equals 5!\n\nGreat job! I have games and quizzes about numbers ready for you. Would you like to try a quiz or play a game?",
        # General
        "hello": "Hello friend! I am Thinkie, your learning buddy!\n\n[Picture: robot]\n\nI am so happy to talk with you! What would you like to learn about today? We have Shapes, Numbers, Colours, and Animals!",
        "hi": "Hello friend! I am Thinkie, your learning buddy!\n\n[Picture: robot]\n\nI am so happy to talk with you! What would you like to learn about today? We have Shapes, Numbers, Colours, and Animals!",
        "hey": "Hello friend! I am Thinkie, your learning buddy!\n\n[Picture: robot]\n\nI am so happy to talk with you! What would you like to learn about today? We have Shapes, Numbers, Colours, and Animals!",
    }
    
    # Check for matches
    for key, val in knowledge.items():
        if key in msg:
            return val
    
    # Fallback responses
    if "quiz" in msg or "test" in msg:
        return "Great! Let me give you a quiz!\n\n[Picture: star]\n\nQuestion: How many sides does a triangle have?\nA) 2\nB) 3\nC) 4\n\nTell me your answer!"
    if "game" in msg or "play" in msg:
        return "Great! I have fun games ready for you! Click on Games in the menu to play, or tell me what topic you want to play about - Shapes, Numbers, or Colours!"
    if "more" in msg or "next" in msg or "continue" in msg:
        return "Let me tell you more!\n\n[Picture: star]\n\nHere is another fun fact: Learning new things makes your brain stronger every day! What topic would you like to explore - Shapes, Numbers, Colours, or Animals?"
    if "bye" in msg or "goodbye" in msg:
        return "Goodbye! You are an amazing learner! Come back anytime you want to learn something new!"
    if "name" in msg:
        return "My name is Thinkie! I am your friendly learning buddy. I love helping you learn new things!"
    
    return "That is interesting! I would love to help you learn.\n\n[Picture: star]\n\nTry asking me about:\n- Animals (lions, elephants, dogs)\n- Colours (red, blue, rainbow)\n- Shapes (circle, triangle, square)\n- Numbers (counting, adding)\n\nWhat would you like to explore?"

@app.route("/guardian")
def guardian():
    if "user" not in session: return redirect(url_for("login"))
    db    = load_db()
    users = {k:v for k,v in db["users"].items() if v.get("role","child")=="child"}
    return render_template("guardian.html", username=session["user"],
                           children=users, topics=list(TOPIC_META.keys()),
                           topic_meta=TOPIC_META)

@app.route("/api/progress/<child>")
def api_progress(child):
    db   = load_db()
    user = db["users"].get(child,{})
    sessions = user.get("sessions",[])
    topic_scores = {}
    for s in sessions:
        t = s.get("topic","")
        topic_scores.setdefault(t,[]).append(s.get("percent",0))
    proficiency = {t:int(sum(v)/len(v)) for t,v in topic_scores.items() if v}
    difficulty  = user.get("difficulty",{t:"Beginner" for t in TOPIC_META})
    return jsonify({"sessions":sessions[-10:],"proficiency":proficiency,
                    "total_quizzes":len(sessions),"difficulty":difficulty})

@app.route("/api/set_difficulty_guardian", methods=["POST"])
def set_difficulty_guardian():
    data  = request.get_json()
    child = data.get("child")
    topic = data.get("topic")
    level = data.get("level","Beginner")
    db    = load_db()
    if child in db["users"]:
        db["users"][child].setdefault("difficulty",{})[topic] = level
        save_db(db)
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5050)
