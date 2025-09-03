import csv

def verify_vehicle(plate):
    try:
        with open('data/vehicles.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['plate'] == plate:
                    return {"found": True, "data": row}
        return {"found": False, "msg": "Vehículo no encontrado"}
    except Exception as e:
        return {"found": False, "msg": str(e)}