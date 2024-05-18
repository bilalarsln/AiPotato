import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# Modelin yüklenmesi
model = tf.keras.models.load_model(r"C:\xampp\htdocs\potato\Potato-Disease_Classification.keras")

# Test edilecek görüntünün yolu
image_path = r"C:\xampp\htdocs\potato\uploads\plantTest.png"



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

# Görüntünün gösterilmesi
plt.imshow(img)
plt.title(f"Predicted: {predicted_class_name}, Confidence: {confidence}")
plt.axis('off')
plt.show()

