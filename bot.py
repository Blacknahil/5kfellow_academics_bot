import os
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from file_manager import generate_drive_config
from file_manager import get_authenticated_drive_service
from file_manager import FileManager
from pathlib import Path
from utils import get_files,load_config_map
from handler import handle_start_step, handle_department_step, handle_year_step, handle_semester_step, handle_stream_step, handle_subject_step, handle_material_step, handle_file_selection_step
from telegram.request import HTTPXRequest

from constants import (
    DEPARTMENTS,
    SOFTWARE_STREAMS,
    ELECTRICAL_STREAMS,
    YEARS,
    SEMESTERS,
    MATERIAL_TYPES,
    SUBJECTS
)

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
    "FILE_SELECTION": "MATERIAL",
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

    print("final state >>> ", state)
    # 🔥 Clear invalid future state
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


# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.effective_chat.id
#     text = update.message.text

#     if chat_id not in user_state:
#         reset_user(chat_id)

#     state = user_state[chat_id]
#     step = state["step"]

#     # ---------------- BACK ---------------- #

#     if text == "⬅️ Back":

#         if step == "DEPARTMENT":
#             await start(update, context)
#             return

#         if step == "YEAR":
#             state["step"] = "DEPARTMENT"
#             await update.message.reply_text(
#                 "Choose your department:",
#                 reply_markup=make_keyboard(DEPARTMENTS, 1)
#             )
#             return

#         if step == "SEMESTER":
#             state["step"] = "YEAR"
#             await update.message.reply_text(
#                 "Select your year:",
#                 reply_markup=make_keyboard(YEARS)
#             )
#             return

#         if step == "STREAM":
#             state["step"] = "SEMESTER"
#             await update.message.reply_text(
#                 "Select semester:",
#                 reply_markup=make_keyboard(SEMESTERS)
#             )
#             return

#         if step == "SUBJECT":
#             if state["stream"]:
#                 state["step"] = "STREAM"
#                 streams = SOFTWARE_STREAMS if state["department"] == "Software Engineering" else ELECTRICAL_STREAMS
#                 await update.message.reply_text(
#                     "Select your stream:",
#                     reply_markup=make_keyboard(streams)
#                 )
#             else:
#                 state["step"] = "SEMESTER"
#                 await update.message.reply_text(
#                     "Select semester:",
#                     reply_markup=make_keyboard(SEMESTERS)
#                 )
#         if step == "MATERIAL":
#             state["step"] = "SUBJECT"
#             await update.message.reply_text(
                
#             )
#             return

#     # ---------------- START ---------------- #

#     if step == "START" and text == "START":
#         state["step"] = "DEPARTMENT"
#         await update.message.reply_text(
#             "Choose your department:",
#             reply_markup=make_keyboard(DEPARTMENTS, 1)
#         )
#         return

#     # ---------------- DEPARTMENT ---------------- #

#     if step == "DEPARTMENT" and text in DEPARTMENTS:
#         state["department"] = text
#         state["step"] = "YEAR"
#         await update.message.reply_text(
#             "Select your year:",
#             reply_markup=make_keyboard(YEARS)
#         )
#         return

#     # ---------------- YEAR ---------------- #

#     if step == "YEAR" and text in YEARS:
#         state["year"] = text
#         state["step"] = "SEMESTER"
#         await update.message.reply_text(
#             "Select semester:",
#             reply_markup=make_keyboard(SEMESTERS)
#         )
#         return

#     # ---------------- SEMESTER ---------------- #

#     if step == "SEMESTER" and text in SEMESTERS:
#         state["semester"] = text

#         # STREAM CONDITIONS
#         if state["department"] == "Software Engineering" and state["year"] in ["4th Year", "5th Year"]:
#             state["step"] = "STREAM"
#             await update.message.reply_text(
#                 "Select your stream:",
#                 reply_markup=make_keyboard(SOFTWARE_STREAMS)
#             )
#             return

#         if (
#             state["department"] == "Electrical Engineering"
#             and (
#                 state["year"] == "5th Year"
#                 or (state["year"] == "4th Year" and text == "2nd Semester")
#             )
#         ):
#             state["step"] = "STREAM"
#             await update.message.reply_text(
#                 "Select your stream:",
#                 reply_markup=make_keyboard(ELECTRICAL_STREAMS)
#             )
#             return

#         # NO STREAM → SUBJECT
#         state["step"] = "SUBJECT"

#         subjects = (
#             SUBJECTS
#             .get(state["department"], {})
#             .get(state["year"], {})
#             .get(state["semester"], ["Demo Subject"])
#         )

#         await update.message.reply_text(
#             "Choose subject:",
#             reply_markup=make_keyboard(subjects, 1)
#         )
#         return

#     # ---------------- STREAM ---------------- #

#     if step == "STREAM":

#         streams = (
#             SOFTWARE_STREAMS
#             if state["department"] == "Software Engineering"
#             else ELECTRICAL_STREAMS
#         )

#         if text in streams:
#             state["stream"] = text
#             state["step"] = "SUBJECT"

#             subjects = (
#                 SUBJECTS
#                 .get(state["department"], {})
#                 .get(state["year"], {})
#                 .get(state["semester"], ["Demo Subject"])
#             )

#             await update.message.reply_text(
#                 "Choose subject:",
#                 reply_markup=make_keyboard(subjects, 1)
#             )
#             return


#     # ---------------- SUBJECT ---------------- #

#     if step == "SUBJECT":

#         subjects = (
#             SUBJECTS
#             .get(state["department"], {})
#             .get(state["year"], {})
#             .get(state["semester"], ["Demo Subject"])
#         )

#         # User is SELECTING subject
#         if text in subjects:
#             state["subject"] = text
#             state["step"] = "MATERIAL"

#             await update.message.reply_text(
#                 "Choose material type:",
#                 reply_markup=make_keyboard(MATERIAL_TYPES)
#             )
#             return

#         # Otherwise just SHOW subjects
#         await update.message.reply_text(
#             "Choose subject:",
#             reply_markup=make_keyboard(subjects, 1)
#         )
#         return


#     # ---------------- MATERIAL ---------------- #

#     if step == "MATERIAL" and text in MATERIAL_TYPES:
#         try:
#             config_map = context.bot_data["config_map"]
#             files = get_files(
#             state["department"],
#             state["year"],
#             state["semester"],
#             state.get("stream"),
#             state["subject"],
#             text,  # ← material type
#             config_map
#             )
#         except KeyError:
#             await update.message.reply_text("No files found for this category.")
#             return
        
#         # Save file list for next step
#         state["step"] = "FILE_SELECTION"
#         state["material_type"] = text
#         state["files"] = files

#         # List files with numbers
#         msg = f"📁 Available {text}:\n\n"
#         for idx, f in enumerate(files, 1):
#             msg += f"{idx}. {f['name']}\n"
#         msg += "\nSend the number of the file you want to download."
#         await update.message.reply_text(msg)
#         return


#     # ---------------- FILE SELECTION ---------------- #
    
#     if step == "FILE_SELECTION":
#         files = state["files"]
#         # Validate the number input
#         if not text.isdigit():
#             await update.message.reply_text("Send a file number.")
#             return
#         idx = int(text) - 1
#         if idx < 0 or idx >= len(files):
#             await update.message.reply_text("Invalid number.")
#             return
#         file_entry= files[idx]
#         drive_id = file_entry["drive_id"]
#         file_manager: FileManager = context.bot_data["file_manager"]
#         await update.message.reply_text("📥 Fetching file...")
        
#         # Send file using FileManager
#         await file_manager.send_file(update, context, drive_id)
#         return 

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text if update.message.text else None

    if chat_id not in user_state:
        reset_user(chat_id)

    state = user_state[chat_id]
    step = state["step"]

    if text == "⬅️ Back":
        print("Handling back action")
        print(f"Current step before back: {state['step']}")
        print("text: ", text)
        handle_back(state)
        print(f"New step after back: {state['step']}")
        new_step = state["step"]
        handler = STEP_HANDLERS.get(new_step)
        print(f"Handler for new step: {handler}")
        if handler:
            print("state: ", state)
            await handler(update, context, state, None)
            print("Back action handled")
        return

    handler = STEP_HANDLERS.get(step)
    if handler:
        await handler(update, context, state, text)


# ---------------- MAIN ---------------- #

def main():
    app = ApplicationBuilder().token(TOKEN).request(request).build()
    
    # google drive service authentication 
    drive_service = get_authenticated_drive_service()
    file_manager = FileManager(app.bot, drive_service)
    config_map = load_config_map(DRIVE_CONFIG_PATH)
    app.bot_data["file_manager"] = file_manager
    app.bot_data["config_map"] = config_map
    

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    # check if the drive config file exists and it aint empty 
    root_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
    path = Path(DRIVE_CONFIG_PATH)
    not_exists_or_empty = not path.exists() or path.stat().st_size == 0
    
    if READ_DRIVE_STATUS:
        print("📂 Drive reading is ENABLED.")
        generate_drive_config(
            root_folder_id=root_folder_id,
            output_path=DRIVE_CONFIG_PATH
            )
        
    elif not READ_DRIVE_STATUS and not_exists_or_empty:
        print("⚠️ Drive reading is DISABLED but the drive config file does not exist or is empty.")
        print("Generating drive config file now...")
        generate_drive_config(
            root_folder_id=root_folder_id,
            output_path=DRIVE_CONFIG_PATH
            )
    else:
        print("📂 Drive reading is DISABLED.")
        print("Using existing drive config file.")
        
    main()