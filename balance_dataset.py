import os
import yaml
import shutil
import random
from collections import Counter
from tqdm import tqdm
from PIL import Image, ImageOps, ImageEnhance

# ----------------- CONFIGURACIÓN ----------------- #

INPUT_DATASET_PATH = "../modelo_detector_partes_dataset/dataset_final_unificado_dp"
OUTPUT_BALANCED_PATH = "../modelo_detector_partes_dataset/dataset_final_balanceado"
BALANCE_STRATEGY = 'percentile' 
BALANCE_TARGET_PERCENTILE = 90.0

AUGMENTATIONS = ['flip', 'brightness', 'none']  # Puedes agregar más: 'rotate', 'color', etc.

# ----------------- FUNCIONES ----------------- #

def analyze_class_distribution(labels_dir):
    class_counts = Counter()
    if not os.path.isdir(labels_dir):
        return class_counts
    for label_file in os.listdir(labels_dir):
        if label_file.endswith(".txt"):
            with open(os.path.join(labels_dir, label_file), 'r') as f:
                for line in f:
                    try:
                        class_id = int(line.strip().split()[0])
                        class_counts[class_id] += 1
                    except (ValueError, IndexError):
                        continue
    return class_counts

def augment_image(img_path, save_path, aug_type='none'):
    img = Image.open(img_path)
    if aug_type == 'flip':
        img = ImageOps.mirror(img)
    elif aug_type == 'brightness':
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(random.uniform(0.7, 1.3))
    img.save(save_path)

def balance_dataset():
    print("--- Iniciando el Proceso de Balanceo de Dataset (Oversampling + Augmentación) ---")
    input_yaml_path = os.path.join(INPUT_DATASET_PATH, "data.yaml")
    if not os.path.exists(input_yaml_path):
        print(f"Error: No se encontró 'data.yaml' en {INPUT_DATASET_PATH}")
        return

    with open(input_yaml_path, 'r') as f:
        data_config = yaml.safe_load(f)
    class_names = data_config.get('names', [])
    if not class_names:
        print("Error: No se encontraron nombres de clases en 'data.yaml'.")
        return

    # Construye la ruta absoluta correcta para las etiquetas de entrenamiento
    train_images_path = os.path.abspath(os.path.join(INPUT_DATASET_PATH, data_config['train']))
    train_labels_path = train_images_path.replace('/images', '/labels')
    print(f"\nAnalizando distribución de clases en: {train_labels_path}")

    original_counts = analyze_class_distribution(train_labels_path)
    if not original_counts:
        print("No se encontraron etiquetas en el set de entrenamiento. Abortando.")
        return

    print("\nDistribución de clases original (entrenamiento):")
    for class_id, count in sorted(original_counts.items()):
        print(f"  - Clase {class_id} ({class_names[class_id]}): {count} instancias")

    counts_list = list(original_counts.values())
    if BALANCE_STRATEGY == 'mean':
        target_count = int(sum(counts_list) / len(counts_list))
    else:
        counts_list.sort()
        percentile_index = int(len(counts_list) * (BALANCE_TARGET_PERCENTILE / 100.0)) - 1
        percentile_index = max(0, min(percentile_index, len(counts_list) - 1))
        target_count = counts_list[percentile_index]

    print(f"\nEstrategia de balanceo: '{BALANCE_STRATEGY}'")
    print(f"Objetivo de instancias por clase: {target_count}")

    print(f"\nCreando estructura de directorios en: {OUTPUT_BALANCED_PATH}")
    os.makedirs(OUTPUT_BALANCED_PATH, exist_ok=True)

    for split in ['valid', 'test']:
        if split in data_config:
            print(f"Copiando conjunto '{split}' sin modificaciones...")
            src_img_dir = os.path.join(INPUT_DATASET_PATH, data_config[split].replace('../', '').replace('./', ''))
            dst_img_dir = os.path.join(OUTPUT_BALANCED_PATH, data_config[split].replace('../', '').replace('./', ''))
            if os.path.exists(dst_img_dir): shutil.rmtree(dst_img_dir)
            if os.path.exists(src_img_dir): shutil.copytree(src_img_dir, dst_img_dir)
            src_lbl_dir = src_img_dir.replace('images', 'labels')
            dst_lbl_dir = dst_img_dir.replace('images', 'labels')
            if os.path.exists(dst_lbl_dir): shutil.rmtree(dst_lbl_dir)
            if os.path.exists(src_lbl_dir): shutil.copytree(src_lbl_dir, dst_lbl_dir)

    print("Balanceando el conjunto 'train' (esto puede tardar)...")
    src_train_img_dir = os.path.abspath(os.path.join(INPUT_DATASET_PATH, os.path.relpath(data_config['train'], '../dataset_final_unificado_dp')))
    src_train_lbl_dir = src_train_img_dir.replace('/images', '/labels')
    dst_train_img_dir = os.path.abspath(os.path.join(OUTPUT_BALANCED_PATH, 'train/images'))
    dst_train_lbl_dir = os.path.abspath(os.path.join(OUTPUT_BALANCED_PATH, 'train/labels'))
    if os.path.exists(dst_train_img_dir): shutil.rmtree(dst_train_img_dir)
    if os.path.exists(dst_train_lbl_dir): shutil.rmtree(dst_train_lbl_dir)
    os.makedirs(dst_train_img_dir)
    os.makedirs(dst_train_lbl_dir)

    for filename in os.listdir(src_train_img_dir):
        shutil.copy(os.path.join(src_train_img_dir, filename), dst_train_img_dir)
    for filename in os.listdir(src_train_lbl_dir):
        shutil.copy(os.path.join(src_train_lbl_dir, filename), dst_train_lbl_dir)

    images_to_duplicate = {class_id: [] for class_id in original_counts.keys()}
    for label_file in os.listdir(src_train_lbl_dir):
        with open(os.path.join(src_train_lbl_dir, label_file), 'r') as f:
            classes_in_file = set()
            for line in f:
                try:
                    classes_in_file.add(int(line.strip().split()[0]))
                except (ValueError, IndexError):
                    continue
            for class_id in classes_in_file:
                images_to_duplicate[class_id].append(os.path.splitext(label_file)[0])

    new_counts = original_counts.copy()
    for class_id, count in tqdm(original_counts.items(), desc="Procesando clases"):
        if count < target_count and count > 0:
            diff = target_count - count
            num_images_for_class = len(images_to_duplicate[class_id])
            if num_images_for_class == 0: continue
            for i in range(diff):
                base_name = random.choice(images_to_duplicate[class_id])
                aug_type = random.choice(AUGMENTATIONS)
                new_base_name = f"{base_name}_aug{i+1}_{class_id}_{aug_type}"
                exts = ['.jpg', '.jpeg', '.png']
                found_ext = None
                for ext in exts:
                    if os.path.exists(os.path.join(src_train_img_dir, base_name + ext)):
                        found_ext = ext
                        break
                if found_ext:
                    src_img_path = os.path.join(src_train_img_dir, base_name + found_ext)
                    dst_img_path = os.path.join(dst_train_img_dir, new_base_name + found_ext)
                    augment_image(src_img_path, dst_img_path, aug_type)
                shutil.copy(
                    os.path.join(src_train_lbl_dir, base_name + ".txt"),
                    os.path.join(dst_train_lbl_dir, new_base_name + ".txt")
                )

    output_yaml_path = os.path.join(OUTPUT_BALANCED_PATH, "data.yaml")
    with open(output_yaml_path, 'w') as f:
        yaml.dump(data_config, f)

    final_counts = analyze_class_distribution(dst_train_lbl_dir)
    print("\n--- Proceso de Balanceo Completado ---")
    print(f"Dataset balanceado guardado en: {OUTPUT_BALANCED_PATH}")
    print("\nDistribución de clases final (entrenamiento):")
    for class_id, count in sorted(final_counts.items()):
        original_c = original_counts.get(class_id, 0)
        print(f"  - Clase {class_id} ({class_names[class_id]}): {count} instancias (Original: {original_c})")

if __name__ == "__main__":
    balance_dataset()