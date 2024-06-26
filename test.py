import tensorflow as tf
import numpy as np

# Modelin yüklenmesi
model = tf.keras.models.load_model("/Users/bilal/Desktop/potato/AiPotato/Potato-Disease_Classification.keras")
#model = tf.keras.models.load_model("/Users/Ilknu/Downloads/AiPotato-main/Potato-Disease_Classification.keras")

def analyze_image(image_path):
    # Görüntünün yüklenmesi ve yeniden boyutlandırılması
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(256, 256))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Giriş boyutunu (1, 256, 256, 3) yapar

    # Görüntünün modelle tahmin edilmesi
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions[0])
    confidence = np.max(predictions[0])
    

    # Sınıf adının alınması
    class_names = ['early blight', 'healthy', 'late blight']  # Sınıf adlarını kendi veri setinize göre güncelleyin
    predicted_class_name = class_names[predicted_class]

    return predicted_class_name, float(confidence)  # confidence değerini float'a dönüştürme
