import random, string, datetime, hashlib

BRANDS = ["Toyota","Mazda","Renault","Chevrolet","Nissan","Kia","Hyundai","Ford","Volkswagen"]
MODELS = ["Corolla","3","Logan","Onix","Versa","Rio","i20","Fiesta","Polo","Duster","Captur"]
COLORS = ["Blanco","Negro","Gris","Rojo","Azul","Plata","Beige"]
INSURERS = ["Sura","Bolivar","AXA","Mapfre","Liberty","Allianz"]
FINE_TYPES = [
    ("EXCESS_SPEED", 6),
    ("RED_LIGHT", 8),
    ("NO_SOAT", 12),
    ("NO_SEATBELT", 4),
    ("PARKING_RESTRICTION", 4),
    ("TECH_REVIEW_EXPIRED", 8)
]
SEVERITIES = ["LOW","MEDIUM","HIGH"]
PARTS_IMPACT = ["front_bumper","rear_bumper","hood","door_left","door_right","trunk","windshield"]

def random_plate():
    return ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=3))

def random_owner_name():
    names = ["Juan","Ana","Pedro","Laura","Carlos","Sofia","Diego","Paula","Miguel","Camila","Andres","Valentina"]
    last = ["Gomez","Perez","Ruiz","Martinez","Sanchez","Torres","Luna","Ramirez","Lopez","Vargas"]
    return random.choice(names) + " " + random.choice(last)

def rand_date_future(days=365):
    base = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=random.randint(15, days))
    return (base + delta).strftime("%Y-%m-%d")

def rand_date_past(days=365*5):
    base = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=random.randint(15, days))
    return (base - delta).strftime("%Y-%m-%d")

def hash_document(name):
    return hashlib.sha256((name + str(random.random())).encode()).hexdigest()[:16]

def gen_fines(max_count=5):
    fines = []
    count = random.randint(0,max_count)
    for _ in range(count):
        t, pts = random.choice(FINE_TYPES)
        amount = round(random.uniform(80, 900) * (pts/4),2)
        fines.append({
            "code": ''.join(random.choices(string.ascii_uppercase+string.digits, k=6)),
            "type": t,
            "amount": amount,
            "issued_at": rand_date_past(900),
            "status": random.choice(["PAID","PENDING","IN_APPEAL"]),
            "points": pts
        })
    return fines

def gen_accidents():
    arr=[]
    for _ in range(random.randint(0,3)):
        arr.append({
            "date": rand_date_past(1500),
            "severity": random.choice(SEVERITIES),
            "part_impacted": random.choice(PARTS_IMPACT),
            "claim_cost": round(random.uniform(200, 5000),2)
        })
    return arr

def gen_claims():
    arr=[]
    for _ in range(random.randint(0,2)):
        arr.append({
            "date": rand_date_past(1200),
            "provider": random.choice(INSURERS),
            "amount": round(random.uniform(150, 4000),2),
            "status": random.choice(["OPEN","CLOSED","REJECTED"])
        })
    return arr

def compute_vehicle_risk(fines, accidents):
    pts = sum(f["points"] for f in fines)
    sev = sum({"LOW":1,"MEDIUM":2,"HIGH":3}[a["severity"]] for a in accidents)
    base = 0.15 + 0.02*pts + 0.04*sev
    return round(min(base, 0.95), 3)

def gen_vehicle_record(plate=None):
    plate = plate or random_plate()
    owner_name = random_owner_name()
    fines = gen_fines()
    accidents = gen_accidents()
    claims = gen_claims()
    risk = compute_vehicle_risk(fines, accidents)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "plate": plate,
        "brand": random.choice(BRANDS),
        "model": random.choice(MODELS),
        "year": random.randint(2012, 2024),
        "color": random.choice(COLORS),
        "vin": ''.join(random.choices(string.ascii_uppercase+string.digits, k=17)),
        "owner_id": hash_document(owner_name),
        "ownership": {
            "owner_name": owner_name,
            "document_hash": hash_document(owner_name),
            "since": rand_date_past(2000)
        },
        "registration": {
            "runt_id": ''.join(random.choices(string.ascii_uppercase+string.digits, k=10)),
            "registered_at": rand_date_past(4000),
            "status": random.choice(["ACTIVE","SUSPENDED","PENDING"])
        },
        "soat": {
            "policy_number": ''.join(random.choices(string.digits, k=12)),
            "insurer": random.choice(INSURERS),
            "expires": rand_date_future(380),
            "active": True
        },
        "tech_review": {
            "center": "CENTRO_"+''.join(random.choices(string.ascii_uppercase, k=3)),
            "expires": rand_date_future(480),
            "passed": True
        },
        "fines": fines,
        "accidents": accidents,
        "claims": claims,
        "risk_score": risk,
        "last_update": now
    }

def gen_driver_record():
    name = random_owner_name()
    infractions=[]
    for _ in range(random.randint(0,4)):
        t, pts = random.choice(FINE_TYPES)
        infractions.append({
            "code": ''.join(random.choices(string.ascii_uppercase+string.digits, k=6)),
            "type": t,
            "points": pts,
            "resolved": random.choice([True, False])
        })
    risk = round(0.1 + 0.05*len(infractions) + random.uniform(0,0.3),3)
    return {
        "driver_id": hash_document(name),
        "name": name,
        "license_category": random.choice(["A2","B1","B2","C1","C2"]),
        "license_expires": rand_date_future(900),
        "years_experience": random.randint(1,25),
        "infractions_history": infractions,
        "accident_count": random.randint(0,5),
        "risk_factor": min(risk,0.95),
        "simulated": True
    }