import os
import subprocess
import whisper
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from loguru import logger
from requests.exceptions import HTTPError
import time
# Настройка логирования через loguru
logger.add("script.log", rotation="500 MB", level="INFO")  # Логи будут сохраняться в файл script.log

# Загрузка переменных окружения из .env файла
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

# Список URL видео на YouTube для обработки
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=9MLisQjCSJc",
    "https://www.youtube.com/watch?v=qHRM5lUFpE8"
]

MODEL = "base"  # Модель Whisper для транскрипции (можно заменить на 'medium' или 'small')
TRANSCRIPTS_DIR = "transcripts"  # Папка для сохранения файлов транскрипций

# Создание папки для транскрипций, если её нет
if not os.path.exists(TRANSCRIPTS_DIR):
    logger.info(f"Создание директории для транскрипций: {TRANSCRIPTS_DIR}")
    os.makedirs(TRANSCRIPTS_DIR)


# Функция загрузки промптов из файлов
def load_prompts(prompt_folder="prompts"):
    """Загружает 4 промпта из папки prompts/ (prompt1.txt - prompt4.txt)."""
    prompts = []
    for n in range(1, 5):
        file_path = os.path.join(prompt_folder, f"prompt{n}.txt")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                prompts.append(f.read().strip())
            logger.info(f"Промпт {n} успешно загружен из {file_path}")
        except FileNotFoundError:
            logger.error(f"Файл {file_path} не найден")
            raise
    return prompts


# Функция извлечения slug (ID видео) из URL YouTube
def extract_slug(youtube_url):
    """Извлекает slug (например, '9MLisQjCSJc') из YouTube URL."""
    parsed_url = urlparse(youtube_url)
    query_params = parse_qs(parsed_url.query)
    slug = query_params.get("v", [None])[0]
    if slug:
        logger.debug(f"Извлечён slug из URL {youtube_url}: {slug}")
    else:
        logger.warning(f"Не удалось извлечь slug из URL: {youtube_url}")
    return slug


# Функция скачивания аудио из YouTube
def download_mp3(youtube_url, output_file):
    """Скачивает аудио в формате MP3 с помощью yt-dlp."""
    command = [
        "yt-dlp", "-x", "--audio-format", "mp3",
        "-o", output_file, youtube_url
    ]
    logger.info(f"Запуск команды для скачивания: {' '.join(command)}")
    subprocess.run(command, check=True)
    logger.info(f"Аудио успешно скачано: {output_file}")


# Функция транскрипции аудио
def transcribe_audio(mp3_file):
    """Транскрибирует MP3-файл с помощью модели Whisper."""
    logger.info(f"Загрузка модели Whisper: {MODEL}")
    model = whisper.load_model(MODEL)
    logger.info(f"Начало транскрипции файла: {mp3_file}")
    result = model.transcribe(mp3_file)
    logger.info(f"Транскрипция завершена для {mp3_file}")
    return result["text"]


# Функция загрузки или создания транскрипции
def load_or_transcribe_audio(slug, youtube_url):
    """Проверяет наличие транскрипции, если нет — скачивает и транскрибирует."""
    transcript_file = os.path.join(TRANSCRIPTS_DIR, f"{slug}.txt")

    # Проверка существования файла транскрипции
    if os.path.exists(transcript_file):
        logger.info(f"Найдена существующая транскрипция: {transcript_file}")
        with open(transcript_file, "r", encoding="utf-8") as f:
            return f.read()

    # Если файла нет, скачиваем и транскрибируем
    audio_file = f"{slug}.mp3"
    logger.info(f"Транскрипция отсутствует, начинаем скачивание: {youtube_url}")
    download_mp3(youtube_url, audio_file)

    transcript = transcribe_audio(audio_file)

    # Сохранение транскрипции в файл
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)
    logger.info(f"Транскрипция сохранена в: {transcript_file}")

    # Удаление временного MP3 файла
    if os.path.exists(audio_file):
        os.remove(audio_file)
        logger.debug(f"Временный файл удалён: {audio_file}")

    return transcript


# Функция генерации ответа через Together.ai
def generate_response(context_text, prompt, max_retries=3):
    full_prompt = f"Контекст:\n{context_text}\n\n{prompt}"
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9,
        "messages": [{"role": "user", "content": full_prompt}]
    }
    for attempt in range(max_retries):
        try:
            logger.debug(f"Отправка запроса к Together.ai (попытка {attempt + 1}/{max_retries})")
            response = requests.post("https://api.together.xyz/v1/chat/completions", headers=HEADERS, json=data)
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            logger.info(f"Ответ от Together.ai получен (длина: {len(result)} символов)")
            return result
        except HTTPError as e:
            if response.status_code == 503 and attempt < max_retries - 1:
                logger.warning(f"Ошибка 503, повторная попытка через 5 секунд...")
                time.sleep(5)
            else:
                logger.error(f"Не удалось получить ответ после {max_retries} попыток: {e}")
                raise


# Функция обработки видео
def process_video(youtube_url, prompts):
    """Обрабатывает видео: транскрибирует и генерирует ответы на промпты."""
    # Извлечение slug из URL
    slug = extract_slug(youtube_url)
    if not slug:
        logger.error(f"Не удалось извлечь slug из URL: {youtube_url}")
        raise ValueError(f"Не удалось извлечь slug из URL: {youtube_url}")

    # Получение или создание транскрипции
    transcript = load_or_transcribe_audio(slug, youtube_url)

    # Генерация ответов для каждого промпта
    outputs = []
    for idx, prompt in enumerate(prompts, 1):
        logger.info(f"Генерация ответа для prompt{idx}")
        result = generate_response(transcript, prompt)
        outputs.append(f"[output prompt {idx}]\n{result}")

    # Сохранение результатов в файл
    output_file = f"{slug}_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(outputs))
    logger.info(f"Результаты сохранены в: {output_file}")

    # Вывод результатов в консоль
    for output in outputs:
        print(output)


# === ОСНОВНОЙ БЛОК ===
logger.info("Запуск скрипта")
prompts = load_prompts()  # Загрузка промптов
logger.info(f"Загружено {len(prompts)} промптов")
for url in YOUTUBE_URLS:
    logger.info(f"Обработка видео: {url}")
    process_video(url, prompts)
logger.info("Скрипт завершён")