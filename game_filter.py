import cv2 as cv # OpenCV kütüphanesini cv olarak import ettim
import numpy as np # NumPy kütüphanesini np olarak import ettim
import random # Rastgele sayı üretmek için random kütüphanesini import ettim
import time # Zaman işlemleri için time kütüphanesini import ettim

# Kamerayı başlatıp ve boyutu ayarladım
video = cv.VideoCapture(0) 
video.set(3, 640) # Genişlik
video.set(4, 480) # Yükseklik

# Kırmızı rengi tanımladım (HSV) ve alt ile üst sınırlarını belirledim (renk aralığı)
lower_kirmizi = np.array([0, 120, 70]) 
upper_kirmizi = np.array([10, 255, 255])

x_oyuncu, y_oyuncu = 320, 400  # Oyuncu başlangıç konumu
dusen_kirmizi = [{'x': random.randint(50, 590), 'y': 0, 'speed': 5}]  # Kırmızı nesnelerin konumları ve hızı
dusen_mavi = {'x': random.randint(50, 590), 'y': 0, 'active': False, 'duration': 0}  # Mavi nesnelerin konumları ve durumu
skor = 0  # Başlangıç skoru
seviye = 1  # Başlangıç seviyesi
baslangic = time.time() # Oyun başlangıç zamanı
kalkan_durum = False # Kalkan aktif değil
kalkan_zaman = 0 # Kalkan süresi

while True:
    ret, frame = video.read() # Kameradan görüntü aldım
    if not ret:
        break
    frame = cv.flip(frame, 1)  # Aynalama efekti
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV) # Renk uzayını değiştirdim
    mask = cv.inRange(hsv, lower_kirmizi, upper_kirmizi) # Kırmızı rengi tespit etmek için maske işlemi
    
    # Kırmızı nesneyi tespit etmek için
    kontur, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # Görüntüdeki kırmızı alanları bulma işlemi
    if kontur:
        en_buyuk_kontur = max(kontur, key=cv.contourArea) # En büyük kırmızı bölgeyi seçtim
        x, y, w, h = cv.boundingRect(en_buyuk_kontur) # En büyük alanı çevreleyen dikdörtgen sınırlarını belirledim
        x_oyuncu = x + w // 2  # Oyuncu konumunu güncelledim
    
    # Zamana göre hız artışı için
    toplam_zaman = time.time() - baslangic # Oyun başlangıcından bu yana geçen süre
    artis_hizi = int(toplam_zaman // 20)  # Her 20 saniyede bir hız arttır
    for nesne in dusen_kirmizi: # Hız artışını uyguladım
        nesne['speed'] = 5 + int(seviye//2) + artis_hizi # Hızın güncellenmesi (seviye ve zaman)

    # Düşen nesneleri hareket ettirmek için
    for nesne in dusen_kirmizi: # Her bir nesne için
        nesne['y'] += nesne['speed'] # Hızı kadar aşağı in
        if nesne['y'] > 480: # Eğer nesne ekranın dışına çıkarsa
            nesne['y'] = 0 # Yeni konumlandırma
            nesne['x'] = random.randint(50, 590) # Yeni konumlandırma
            skor += 1  # Puan 1 arttırdım
            if skor % 5 == 0:  # Her 5 puanda seviyeyi arttırdım
                seviye += 1
                dusen_kirmizi.append({'x': random.randint(50, 590), 'y': 0, 'speed': 5 + int(seviye//2)+artis_hizi})  # Yeni nesne ekledim
    
    # Kalkan nesnesini hareket ettirmek için
    dusen_mavi['y'] += 5 # Hızı kadar aşağı in (sabit hız)
    if dusen_mavi['y'] > 480 or kalkan_durum: # Eğer nesne ekranın dışına çıkarsa veya kalkan aktifse
        dusen_mavi['y'] = -100 # Yeni konumlandırma
        dusen_mavi['x'] = random.randint(50, 590) # Yeni konumlandırma
    
    # Kalkanı alıp aktif etmek için
    if abs(x_oyuncu - dusen_mavi['x']) < 40 and abs(y_oyuncu - dusen_mavi['y']) < 40: # Eğer oyuncu kalkanı alırsa (çarpışma kontrolü) 
        kalkan_durum = True # Kalkanı aktif et
        kalkan_zaman = time.time() # Kalkanın aktif olduğu zamanı kaydet
        dusen_mavi['y'] = -100  # Kalkanı yukarı çıkar
    
    # Kalkan süresi kontrolü için (5 saniye aktif)
    if kalkan_durum and time.time() - kalkan_zaman > 5: # Eğer kalkan aktifse ve 5 saniye geçtiyse
        kalkan_durum = False # Kalkanı bitir
    
    # Kırmızı için çarpışma kontrolü
    for nesne in dusen_kirmizi: # Her bir nesne için
        if abs(x_oyuncu - nesne['x']) < 40 and abs(y_oyuncu - nesne['y']) < 40: # Eğer oyuncu kırmızı nesneye çarparsa (çarpışma kontrolü)
            if not kalkan_durum: # Eğer kalkan aktif değilse
                print(f"Oyun Bitti! Skor: {skor} , Seviye: {seviye}") # Oyun bitti mesajı ve skor bilgisi
                video.release() # Kamerayı kapat
                cv.destroyAllWindows() # Pencereyi kapat
                exit() # Programı sonlandır
    
    # Oyuncu ve düşen kırmızı nesneleri çizdim
    cv.circle(frame, (x_oyuncu, y_oyuncu), 20, (0, 255, 0), -1) # Oyuncuyu çiz (yeşil)
    for nesne in dusen_kirmizi: 
        cv.circle(frame, (nesne['x'], nesne['y']), 20, (0, 0, 255), -1) # Düşen nesneleri çiz (kırmızı)
    
    # Kalkan nesnesini çizdim
    cv.circle(frame, (dusen_mavi['x'], dusen_mavi['y']), 20, (255, 0, 0), -1) # Kalkanı çiz (mavi)
    
    # Puanı ve seviyeyi gösterdim
    cv.putText(frame, f'Skor: {skor}', (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2) # Puanı anlık olarak ekranda gösterdim
    cv.putText(frame, f'Seviye: {seviye}', (20, 80), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2) # Seviyeyi anlık olarak ekranda gösterdim
    if kalkan_durum: # Eğer kalkan aktifse
        cv.putText(frame, 'Kalkan Aktif!(5 sn)', (20, 120), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2) # Kalkan aktif yazısını ekranda gösterdim
    
    cv.imshow('Tiktok Nesne Oyunu Filtresi', frame) # Oyun penceresini gösterdim
    if cv.waitKey(1) == ord('q'): # Eğer 'q' tuşuna basılırsa kapat
        break

video.release() # Kamerayı kapat
cv.destroyAllWindows() # Pencereyi kapat