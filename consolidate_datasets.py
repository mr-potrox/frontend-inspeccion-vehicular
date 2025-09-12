import os
import yaml
import shutil
from sklearn.model_selection import train_test_split

# --- CONFIGURACIÓN PRINCIPAL ---
# Este script ahora tiene un único propósito: crear el dataset maestro para el DETECTOR DE DAÑOS.

# 1. Clases maestras para los DAÑOS.
MASTER_CLASSES = ['scratch', 'dent', 'broken_glass']

# 2. Lista definitiva de datasets de DAÑOS.
SOURCES = [
    {
        "name": "Roboflow_Car_Damage_VYHVW", # El más detallado
        "path": "datasets_fuente/Roboflow_Car_Damage_Detection_VYHVW", # <-- USA TUS RUTAS
        "class_map": { 
            0: "bumper-dent", 1: "bumper-scratch", 2: "door-dent", 
            3: "door-scratch", 4: "glass-shatter", 5: "head-lamp", 
            6: "hood-dent", 7: "hood-scratch", 8: "rear-lamp", 
            9: "tail-lamp"
        },
        "translation_logic": {
            "bumper-dent": "dent", "door-dent": "dent", "hood-dent": "dent",
            "bumper-scratch": "scratch", "door-scratch": "scratch", "hood-scratch": "scratch",
            "glass-shatter": "broken_glass"
        }
    },
    {
        "name": "Roboflow_Damage_WSRIL", # Buen dataset base
        "path": "datasets_fuente/Roboflow_Car_Damage_Detection_WSRIL", # <-- USA TUS RUTAS
        "class_map": { 0: "damage", 1: "dent", 2: "scratch" },
        "translation_logic": { "damage": "dent" }
    },
    {
        "name": "Roboflow_Scratch_BB", # Especialista en arañazos
        "path": "datasets_fuente/Roboflow_Car_Scratch_BB", # <-- USA TUS RUTAS
        "class_map": { 0: "scratch" }
    },
    {
        "name": "Roboflow_Damage_AENQ5", # Aporta diversidad de imágenes
        "path": "datasets_fuente/Roboflow_Car_Damage_AENQ5", # <-- USA TUS RUTAS
        "class_map": { 0: "damage" },
        "translation_logic": { "damage": "dent" }
    },
    {
        "name": "Roboflow_Scratch_PIZJ9", # Otro especialista en arañazos
        "path": "datasets_fuente/Roboflow_Car_Scratch_PIZJ9", # <-- USA TUS RUTAS
        "class_map": { 0: "car scratch" },
        "translation_logic": { "car scratch": "scratch" }
    }
]

# 3. Carpeta de salida para el dataset de DAÑOS.
OUTPUT_DIR = "dataset_maestro_danos" # Cambiado para mayor claridad
TRAIN_RATIO = 0.8  # 80% para entrenamiento, 20% para validación.


# --- TU LÓGICA MEJORADA (Mantenida porque es excelente) ---

def main():
    print("Iniciando la consolidación de datasets de DAÑOS...")

    # Validar rutas de fuentes
    for source in SOURCES:
        if not os.path.exists(source["path"]):
            print(f"ADVERTENCIA: La ruta '{source['path']}' para el dataset '{source['name']}' no existe. Omitiendo.")
            continue # Se añade 'continue' para que no procese una ruta inexistente

    # Crear estructura de carpetas de salida
    os.makedirs(os.path.join(OUTPUT_DIR, "images/train"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "images/val"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "labels/train"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "labels/val"), exist_ok=True)

    all_images = []

    for source in SOURCES:
        if not os.path.exists(source["path"]):
            continue
        print(f"\nProcesando fuente: {source['name']}")
        source_train_images = os.path.join(source['path'], 'train/images')
        source_val_images = os.path.join(source['path'], 'valid/images')

        source_images_paths = []
        if os.path.exists(source_train_images):
            for f in os.listdir(source_train_images):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                    source_images_paths.append(os.path.join(source_train_images, f))
        if os.path.exists(source_val_images):
            for f in os.listdir(source_val_images):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                    source_images_paths.append(os.path.join(source_val_images, f))

        for img_path in source_images_paths:
            base_filename = os.path.basename(img_path)
            name, ext = os.path.splitext(base_filename)
            label_filename = f"{name}.txt"
            label_dir = os.path.dirname(img_path).replace("images", "labels")
            original_label_path = os.path.join(label_dir, label_filename)

            if not os.path.exists(original_label_path):
                continue

            unique_filename = f"{source['name']}_{base_filename}"
            all_images.append({
                "original_img_path": img_path,
                "original_label_path": original_label_path,
                "unique_filename": unique_filename,
                "source": source
            })

    print(f"\nSe encontraron un total de {len(all_images)} imágenes.")

    if not all_images:
        print("ERROR: No se encontraron imágenes válidas en ninguna de las rutas de dataset especificadas.")
        print("Por favor, verifica que las rutas en la variable 'SOURCES' sean correctas y que los directorios contengan imágenes y sus archivos de etiquetas correspondientes.")
        return # Salir si no hay imágenes para procesar

    train_files, val_files = train_test_split(all_images, train_size=TRAIN_RATIO, random_state=42)
    print(f"Dividiendo en {len(train_files)} para entrenamiento y {len(val_files)} para validación.")

    process_files(train_files, "train")
    process_files(val_files, "val")

    create_final_yaml()
    summarize_labels()

    print("\n¡Proceso de consolidación completado exitosamente!")
    print(f"Tu dataset maestro está listo en la carpeta: '{OUTPUT_DIR}'")

def process_files(files, split):
    print(f"Procesando {split} set...")
    for file_info in files:
        source = file_info['source']
        dest_img_path = os.path.join(OUTPUT_DIR, f"images/{split}", file_info['unique_filename'])
        try:
            shutil.copy(file_info['original_img_path'], dest_img_path)
        except Exception as e:
            print(f"Error copiando imagen {file_info['original_img_path']}: {e}")
            continue

        new_labels = []
        try:
            with open(file_info['original_label_path'], 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split()
                    if not parts: continue
                    try:
                        original_class_id = int(parts[0])
                    except (ValueError, IndexError):
                        print(f"Advertencia: línea inválida en {file_info['original_label_path']}: '{line.strip()}'")
                        continue

                    original_class_name = source['class_map'].get(original_class_id)
                    if not original_class_name:
                        continue

                    translated_name = source.get("translation_logic", {}).get(original_class_name, original_class_name)
                    if translated_name in MASTER_CLASSES:
                        master_class_id = MASTER_CLASSES.index(translated_name)
                        new_labels.append(f"{master_class_id} {' '.join(parts[1:])}")
        except Exception as e:
            print(f"Error leyendo etiqueta {file_info['original_label_path']}: {e}")
            continue

        if new_labels:
            label_name, _ = os.path.splitext(file_info['unique_filename'])
            dest_label_path = os.path.join(OUTPUT_DIR, f"labels/{split}", f"{label_name}.txt")
            try:
                with open(dest_label_path, 'w') as f:
                    f.write("\n".join(new_labels))
            except Exception as e:
                print(f"Error escribiendo etiqueta {dest_label_path}: {e}")

def create_final_yaml():
    yaml_content = {
        'train': os.path.abspath(os.path.join(OUTPUT_DIR, 'images/train')),
        'val': os.path.abspath(os.path.join(OUTPUT_DIR, 'images/val')),
        'nc': len(MASTER_CLASSES),
        'names': MASTER_CLASSES
    }
    with open(os.path.join(OUTPUT_DIR, 'data.yaml'), 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)

def summarize_labels():
    from collections import Counter
    counter = Counter()
    for split in ['train', 'val']:
        labels_dir = os.path.join(OUTPUT_DIR, f'labels/{split}')
        if not os.path.exists(labels_dir): continue
        for fname in os.listdir(labels_dir):
            with open(os.path.join(labels_dir, fname)) as f:
                for line in f:
                    if line.strip():
                        class_id = line.strip().split()[0]
                        counter[class_id] += 1
    print("\nResumen de clases en el dataset de DAÑOS maestro:")
    for idx, name in enumerate(MASTER_CLASSES):
        print(f"  {name}: {counter.get(str(idx), 0)} etiquetas")

if __name__ == "__main__":
    main()

