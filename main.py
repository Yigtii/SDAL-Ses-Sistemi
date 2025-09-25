import time
import pygame
import datetime
import threading
import os


def play_sound_loop(filename, duration):
    """Ses dosyasını belirtilen süre boyunca döngüde çal"""
    try:
        if not os.path.exists(filename):
            print(f"❌ Ses dosyası bulunamadı: {filename}")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(filename)

        start_time = time.time()
        while time.time() - start_time < duration:
            print(f"🔊 {filename} çalınıyor (döngüde)...")
            pygame.mixer.music.play()

            # Şarkı bitene kadar veya süre dolana kadar bekle
            while pygame.mixer.music.get_busy():
                if time.time() - start_time >= duration:
                    pygame.mixer.music.stop()
                    return
                time.sleep(0.1)

            # Şarkı bitti, başa sar ve tekrar çal
            print("🔄 Şarkı bitti, başa sarılıyor...")

    except Exception as e:
        print(f"❌ Ses çalınırken hata oluştu: {e}")


def play_sound_once(filename):
    """Ses dosyasını bir kerelik çal"""
    try:
        if not os.path.exists(filename):
            print(f"❌ Ses dosyası bulunamadı: {filename}")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        print(f"🔊 {filename} çalınıyor...")

        # Ses bitene kadar bekle
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    except Exception as e:
        print(f"❌ Ses çalınırken hata oluştu: {e}")


def calculate_times():
    """Ders ve teneffüs zamanlarını hesapla"""
    schedule = []

    # Sabah dersleri (1-5. dersler)
    start_time = datetime.datetime.strptime("08:00", "%H:%M")

    for i in range(1, 6):
        lesson_end = start_time + datetime.timedelta(minutes=40)

        # Ders başlangıç sesi (sadece ilk ders için)
        if i == 1:
            schedule.append(("08:00", "1. Ders Başlangıç", "baslangic.mp3", False))

        # Ders bitiş
        if i == 5:
            # 5. ders bitişinde öğle arası başlangıç sesi
            schedule.append((lesson_end.strftime("%H:%M"), f"{i}. Ders Bitiş", "bitis2.mp3", False))
        else:
            schedule.append((lesson_end.strftime("%H:%M"), f"{i}. Ders Bitiş", None, False))

            # Teneffüs (5. ders hariç) - 10 dakika şarkı çalacak
            teneffus_start = lesson_end
            teneffus_end = teneffus_start + datetime.timedelta(minutes=10)

            # Teneffüs başlangıcında şarkıyı başlat
            schedule.append((teneffus_start.strftime("%H:%M"), f"{i}. Ders Sonrası Teneffüs", "sarki.mp3", True))

            if i < 5:  # 4. ders sonrası normal teneffüs
                next_lesson_start = teneffus_end
                schedule.append((next_lesson_start.strftime("%H:%M"), f"{i + 1}. Ders Başlangıç", None, False))
            else:  # 5. ders sonrası öğle arası
                next_lesson_start = teneffus_end + datetime.timedelta(minutes=45)  # 45 dakika öğle arası
                schedule.append(("12:45", "6. Ders Başlangıç (Öğle Arası Bitiş)", "baslangic1.mp3", False))

            start_time = next_lesson_start

    # Öğleden sonra dersleri (6-8. dersler)
    start_time = datetime.datetime.strptime("12:45", "%H:%M")

    for i in range(6, 9):
        lesson_end = start_time + datetime.timedelta(minutes=40)

        # Ders bitiş
        if i == 8:
            # 8. ders bitişinde GÜN SONU - sadece bitis2.mp3 çalacak
            schedule.append((lesson_end.strftime("%H:%M"), "8. Ders Bitiş (GÜN SONU)", "bitis2.mp3", False))
            # Son ders olduğu için teneffüs YOK
        else:
            schedule.append((lesson_end.strftime("%H:%M"), f"{i}. Ders Bitiş", None, False))

            # Teneffüs - 10 dakika şarkı çalacak (sadece 6 ve 7. dersler sonrası)
            teneffus_start = lesson_end
            teneffus_end = teneffus_start + datetime.timedelta(minutes=10)
            next_lesson_start = teneffus_end

            # Teneffüs başlangıcında şarkıyı başlat
            schedule.append((teneffus_start.strftime("%H:%M"), f"{i}. Ders Sonrası Teneffüs", "sarki.mp3", True))

            schedule.append((next_lesson_start.strftime("%H:%M"), f"{i + 1}. Ders Başlangıç", None, False))
            start_time = next_lesson_start

    return schedule


def main():
    print("Ders Zamanlayıcı Başlatıldı")
    print("Teneffüslerde 10 dakika BOYUNCA şarkı çalacak 🎵")
    print("15:05'te GÜN SONU - bitis2.mp3 çalacak 🏁")
    print("=" * 50)

    # Mevcut dizindeki dosyaları kontrol et
    current_dir = os.getcwd()
    print(f"📁 Çalışma dizini: {current_dir}")
    print("📂 Dizindeki dosyalar:")
    for file in os.listdir():
        if file.endswith('.mp3'):
            print(f"   🎵 {file}")
    print("=" * 50)

    schedule = calculate_times()

    # Programı göster
    for time_str, event, sound, is_teneffus in schedule:
        print(f"{time_str} - {event}")
        if sound:
            if is_teneffus:
                print(f"  🎵 10 dakika BOYUNCA şarkı çalacak: {sound}")
            else:
                print(f"  🔔 Ses çalınacak: {sound}")

    print("\nZamanlayıcı çalışıyor... (Çıkmak için Ctrl+C)")
    print("=" * 50)

    # Aktif şarkı thread'ini takip etmek için
    active_music_thread = None

    try:
        while True:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_time_with_seconds = now.strftime("%H:%M:%S")

            # Debug için her dakika zamanı göster
            if now.second == 0:
                print(f"⏰ Şu anki zaman: {current_time_with_seconds} - Beklenen sonraki olaylar:")
                for time_str, event, sound, is_teneffus in schedule[:3]:
                    print(f"   {time_str} - {event}")

            for time_str, event, sound, is_teneffus in schedule:
                if current_time == time_str:
                    print(f"\n🎯 {current_time} - {event}")

                    if sound:
                        if is_teneffus:
                            # Teneffüs şarkısı - 10 dakika BOYUNCA döngüde çal
                            print(f"  🎵 10 dakika BOYUNCA şarkı çalınıyor: {sound}")
                            if active_music_thread and active_music_thread.is_alive():
                                print("  ⏹️ Önceki şarkı durduruluyor...")
                                pygame.mixer.music.stop()
                                active_music_thread.join(timeout=1.0)

                            active_music_thread = threading.Thread(
                                target=play_sound_loop,
                                args=(sound, 600)  # 600 saniye = 10 dakika
                            )
                            active_music_thread.daemon = True
                            active_music_thread.start()
                        else:
                            # Normal ses efekti (bir kerelik)
                            print(f"  🔊 {sound} çalınıyor...")
                            sound_thread = threading.Thread(target=play_sound_once, args=(sound,))
                            sound_thread.daemon = True
                            sound_thread.start()

                    # Bu olayı işledik, bir sonraki kontrol için bekle
                    schedule.remove((time_str, event, sound, is_teneffus))
                    print(f"  ✅ Olay işlendi, kalan olay sayısı: {len(schedule)}")
                    break

            time.sleep(10)  # 10 saniyede bir kontrol et

    except KeyboardInterrupt:
        print("\n\nProgram sonlandırıldı.")
        # Program kapanırken müziği durdur
        try:
            pygame.mixer.music.stop()
        except:
            pass


if __name__ == "__main__":
    main()