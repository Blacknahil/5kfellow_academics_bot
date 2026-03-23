import os
import time
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.request import HTTPXRequest
from file_manager import load_config, FileManager, get_authenticated_drive_service
from handler import handle_start_step, handle_department_step, handle_year_step, handle_semester_step
from handler import handle_stream_step, handle_subject_step, handle_material_step, handle_file_selection_step, stats_command
from analytics.tracker import track_request, track_user
from analytics.init_tables import ensure_analytics_tables


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

READ_DRIVE_STATUS = os.getenv("READ_DRIVE_STATUS") == "True"
DRIVE_CONFIG_PATH = "config/drive_config.json"

request = HTTPXRequest(
    connect_timeout=30,
    read_timeout=180,
    write_timeout=180,
    pool_timeout=180,
)

# ---------------- STATE ---------------- #

user_state = {}


def reset_user(chat_id):
    user_state[chat_id] = {
        "step": "START",
        "department": None,
        "year": None,
        "semester": None,
        "stream": None,
        "subject": None,
        "material_type": None,
        "files": None,
    }

# ---------------- BACK TRANSITIONS LOGIC ---------------- #

BACK_TRANSITIONS = {
    "DEPARTMENT": "START",
    "YEAR": "DEPARTMENT",
    "SEMESTER": "YEAR",
    "STREAM": "SEMESTER",
    "SUBJECT": lambda s: "STREAM" if s["stream"] else "SEMESTER",
    "MATERIAL": "SUBJECT",
    "FILE_SELECTION": lambda s: "DEPARTMENT" if s["department"] == "book_club" else "MATERIAL",
}

STATE_CLEANUP = {
    "START": ["department", "year", "semester", "stream", "subject", "material_type", "files"],
    "DEPARTMENT": ["year", "semester", "stream", "subject", "material_type", "files"],
    "YEAR": ["semester", "stream", "subject", "material_type", "files"],
    "SEMESTER": ["stream", "subject", "material_type", "files"],
    "STREAM": ["subject", "material_type", "files"],
    "SUBJECT": ["material_type", "files"],
    "MATERIAL": ["files"],
}

def handle_back(state):
    current = state["step"]
    prev = BACK_TRANSITIONS.get(current)

    if not prev:
        return

    new_step = prev(state) if callable(prev) else prev
    state["step"] = new_step

    # Clear invalid future state
    for key in STATE_CLEANUP.get(new_step, []):
        state[key] = None


STEP_HANDLERS = {
    "START": handle_start_step,
    "DEPARTMENT": handle_department_step,
    "YEAR": handle_year_step,
    "SEMESTER": handle_semester_step,
    "STREAM": handle_stream_step,
    "SUBJECT": handle_subject_step,
    "MATERIAL": handle_material_step,
    "FILE_SELECTION": handle_file_selection_step,
}



# ---------------- HANDLERS ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    reset_user(chat_id)

    await update.message.reply_text(
        "🎓 Welcome to 5kilo Academic Material Bot\n\nPress START to continue.",
        reply_markup=ReplyKeyboardMarkup([["START"]], resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text if update.message.text else None

    if chat_id not in user_state:
        reset_user(chat_id)

    state = user_state[chat_id]
    step = state["step"]
    
    user_id = update.effective_user.id
    try:
        await track_user(user_id)
        await track_request()
    except Exception as e:
        print("Error tracking analytics: ", e)
    
    if text == "⬅️ Back": 
        # Handle back action
        handle_back(state)
        new_step = state["step"]
        handler = STEP_HANDLERS.get(new_step)

        if handler:
            await handler(update, context, state, "back")
        return

    handler = STEP_HANDLERS.get(step)
    if handler:
        await handler(update, context, state, text)


# ---------------- MAIN ---------------- #

def main(config_map: dict):
    app = ApplicationBuilder().token(TOKEN).request(request).build()
    
    # google drive service authentication 
    drive_service = get_authenticated_drive_service()
    file_manager = FileManager(app.bot, drive_service)

    app.bot_data["file_manager"] = file_manager
    app.bot_data["config_map"] = config_map
    

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    # check if the drive config file exists and it aint empty 
    root_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
    if root_folder_id is None:
        raise RuntimeError("GOOGLE_DRIVE_ROOT_FOLDER_ID environment variable is not set.")
    
    config_load_started_at = time.perf_counter()
    config_map = load_config(
        READ_DRIVE_STATUS,
        root_folder_id,
        DRIVE_CONFIG_PATH
    )
    config_load_elapsed_seconds = time.perf_counter() - config_load_started_at
    print(
        "Config map loaded in "
        f"{config_load_elapsed_seconds:.2f}s "
        f"({config_load_elapsed_seconds / 60:.2f} min)."
    )
    
    try:
        ensure_analytics_tables()
    except Exception as e:
        print("Error ensuring analytics tables: ", e)
        
    main(config_map)