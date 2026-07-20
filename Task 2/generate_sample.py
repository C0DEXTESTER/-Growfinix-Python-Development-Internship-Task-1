"""
Generates a realistic, messy sample log file of tour enquiries.
Run once to produce sample_enquiries.txt -- this is just test-data
generation, NOT part of the actual CLI tool (see log_parser.py for that).
"""
import random

random.seed(42)

FIRST_NAMES = ["John", "Priya", "Robert", "Aisha", "Carlos", "Mei", "David",
               "Fatima", "Liam", "Sofia", "Arjun", "Emma", "Kenji", "Olga",
               "Noah", "Zara", "Mohammed", "Grace", "Ivan", "Chloe"]
LAST_NAMES = ["Smith", "Kapoor", "Johnson", "Khan", "Rodriguez", "Chen",
              "Miller", "Ahmed", "O'Brien", "Rossi", "Mehta", "Davis",
              "Tanaka", "Petrova", "Wilson", "Ali", "Hussain", "Taylor",
              "Petrov", "Bennett"]
DESTINATIONS = ["Bali", "Paris", "Goa", "London", "Dubai", "Bangkok", "Rome",
                "Tokyo", "New York", "Maldives", "Switzerland", "Singapore",
                "Kerala", "Manali", "Kashmir", "Sydney"]
# a few "unlisted" destinations to test the fallback/unknown path
UNLISTED_DESTINATIONS = ["Atlantis", "Narnia Hills", "Wakanda Falls"]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "proton.me"]


def make_email(first, last):
    style = random.choice([
        f"{first.lower()}.{last.lower()}",
        f"{first.lower()}{last.lower()}",
        f"{first.lower()}{random.randint(1,99)}",
        f"{first[0].lower()}.{last.lower()}",
    ])
    style = style.replace("'", "")
    return f"{style}@{random.choice(EMAIL_DOMAINS)}"


TEMPLATES = [
    # (template string using {name} {email} {dest}, needs_name, needs_email, needs_dest)
    "Enquiry #{eid} - Hi, I'm {name} ({email}) and I'd like to book a tour to {dest} sometime next month.",
    "Name: {name}\nEmail: {email}\nDestination: {dest}\nMessage: Please send me a quote ASAP.",
    "Hey team, this is {name} - reach me at {email}. Thinking about a {dest} trip!! Any deals??",
    "To whom it may concern, my name is {name} and my email id is {email}. Kindly share packages for {dest}.",
    "*** NEW LEAD ***\nFrom: {name} <{email}>\nInterested in: {dest}\nSource: Website Form",
    "hi im {name}, wanted to ask about group tours to {dest}. my mail - {email}",
    "Enquiry submitted by {name} ({email}) regarding upcoming {dest} vacation package. Please call back.",
    "Dear Sir/Madam,\nMyself {name}, I am planning a trip to {dest} with family of 4.\nContact: {email}\nRegards.",
]

# Templates with a field intentionally missing (to test partial parsing)
NO_EMAIL_TEMPLATES = [
    "Enquiry #{eid} - {name} called in asking about {dest} packages, said will email later.",
    "Walk-in enquiry: {name}, interested in {dest} tour, no contact email provided.",
]
NO_NAME_TEMPLATES = [
    "Enquiry #{eid} - someone reached out from {email} asking about {dest} tour packages, name not caught on call.",
]
NO_DEST_TEMPLATES = [
    "Enquiry #{eid} - {name} ({email}) asked general questions about international tour packages, no specific place mentioned yet.",
]

# Pure noise lines mixed into the file (unparsable junk, headers, separators)
NOISE_LINES = [
    "-------------------------------------------------",
    "=== LOG EXPORT :: tour_enquiries_raw_dump.txt ===",
    "[SYSTEM] Auto-backup completed at 03:00 AM",
    "",
    "NOTE: duplicate entries below may exist due to form resubmission",
    "###",
    "[WARN] Entry corrupted during export, skipping...",
    "asdkjaslkjd 12903 !!! ??? corrupted_record_0x00",
    "",
]

lines = []
lines.append("=== RAW TOUR ENQUIRY LOG EXPORT ===")
lines.append(f"Generated: 2026-07-18 | Records: (see below) | Format: UNSTRUCTURED\n")

eid = 1000
entries_to_generate = 55

for i in range(entries_to_generate):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    email = make_email(first, last)
    dest = random.choice(DESTINATIONS)
    eid += 1

    roll = random.random()
    if roll < 0.72:
        tmpl = random.choice(TEMPLATES)
        entry = tmpl.format(eid=eid, name=name, email=email, dest=dest)
    elif roll < 0.82:
        tmpl = random.choice(NO_EMAIL_TEMPLATES)
        entry = tmpl.format(eid=eid, name=name, dest=dest)
    elif roll < 0.90:
        tmpl = random.choice(NO_NAME_TEMPLATES)
        entry = tmpl.format(eid=eid, email=email, dest=dest)
    elif roll < 0.95:
        tmpl = random.choice(NO_DEST_TEMPLATES)
        entry = tmpl.format(eid=eid, name=name, email=email)
    else:
        # unlisted / unknown destination
        tmpl = random.choice(TEMPLATES)
        entry = tmpl.format(eid=eid, name=name, email=email, dest=random.choice(UNLISTED_DESTINATIONS))

    lines.append(entry)

    # occasionally sprinkle in noise
    if random.random() < 0.35:
        lines.append(random.choice(NOISE_LINES))
    lines.append("")  # blank line separates enquiry blocks

# A couple of fully garbage / totally unparsable blocks
lines.append("435098 corrupted binary junk >>>> 0xFFDD sync error retry=3")
lines.append("")
lines.append("Random unrelated customer feedback: 'Great service, loved the hotel!' -- not an enquiry.")
lines.append("")

with open("sample_enquiries.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Generated sample_enquiries.txt with {entries_to_generate} enquiry blocks + noise.")
