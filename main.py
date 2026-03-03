import yt_dlp
import json
import os
import sys
import shutil
from pathlib import Path

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg.exe")
    
    ffmpeg_exe = shutil.which("ffmpeg")
    if ffmpeg_exe:
        return ffmpeg_exe
    
    return "ffmpeg"


if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

SETTINGS_FILE = BASE_DIR / "settings.json"
DEFAULT_PATH = str(BASE_DIR)



# ---------- SETTINGS ----------
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        settings = {"download_path": DEFAULT_PATH}
        save_settings(settings)
        return settings

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("⚠️ settings.json повреждён, пересоздаю файл")
        settings = {"download_path": DEFAULT_PATH}
        save_settings(settings)
        return settings



def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def settings_menu(settings):
    while True:
        print("\n⚙️ НАСТРОЙКИ")
        print(f"📂 Текущий путь сохранения:\n{settings['download_path']}\n")

        print("0) ⬅ Вернуться в главное меню")
        print("1) Изменить путь сохранения")

        choice = input("Номер: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            print("\nФормат ввода пути:")
            print(" Linux:   /home/user/Videos")
            print(" Windows: C:/Users/User/Videos\n")

            new_path = input("Введи новый путь: ").strip()
            path = Path(new_path).expanduser()

            if path.exists() and path.is_dir():
                settings["download_path"] = str(path.resolve())
                save_settings(settings)
                print("✅ Путь сохранения обновлён")
            else:
                print("❌ Путь не существует или это не папка")

        else:
            print("❌ Неверный выбор")


# ---------- DOWNLOAD ----------
def choose_options(choice: str):
    if choice == "1":
        return {
            "format": "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best",
            "merge_output_format": "mp4",
        }

    elif choice == "2":
        return {
            "format": "bv*[ext=webm]+ba[ext=webm]/bv*+ba/best",
            "merge_output_format": "webm",
        }

    elif choice == "3":
        return {
            "format": "ba[ext=m4a]/ba/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }],
        }

    return None


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"\r⬇ {percent} | {speed} | ETA {eta}", end="")
    elif d["status"] == "finished":
        print("\n✅ Скачивание завершено")


def download_flow(choice, settings):
    url = input("\nВставь ссылку на YouTube видео: ").strip()
    opts = choose_options(choice)

    if not opts:
        print("❌ Неверный выбор")
        return

    ydl_opts = {
        "outtmpl": os.path.join(settings["download_path"], "%(title)s.%(ext)s"),
        "noplaylist": True,
        "progress_hooks": [progress_hook],
        "quiet": False,
        "ffmpeg_location": get_ffmpeg_path(),
        **opts
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# ---------- MAIN LOOP ----------
def main():
    settings = load_settings()
    
    ffmpeg_path = get_ffmpeg_path()
    print(f"\n🔧 FFmpeg: {ffmpeg_path}")
    
    if ffmpeg_path == "ffmpeg" or not os.path.isfile(ffmpeg_path):
        print("⚠️  Предупреждение: ffmpeg может быть не найден!")
        print("   Убедитесь, что ffmpeg установлен и доступен в PATH")

    while True:
        print("\n📥 YOUTUBE DOWNLOADER")
        print("1) Видео MP4 — максимальное качество")
        print("2) Видео WEBM — максимальное качество")
        print("3) Только аудио → M4A (AAC)")
        print("4) ⚙️ Настройки")
        print("9) ❌ Выход")

        choice = input("Номер: ").strip()

        if choice == "9":
            print("👋 Завершение работы")
            break

        elif choice == "4":
            settings_menu(settings)

        elif choice in {"1", "2", "3"}:
            download_flow(choice, settings)

        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    main()