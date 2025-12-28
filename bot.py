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
from drive_config_builder.main import generate_drive_config
from pathlib import Path

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
DRIVE_CONFIG_PATH = "output/drive_config.json"

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
    }


# ---------------- KEYBOARD ---------------- #

def make_keyboard(options, cols=2, back=True):
    keyboard, row = [], []

    for opt in options:
        row.append(opt)
        if len(row) == cols:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    if back:
        keyboard.append(["⬅️ Back"])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


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
    text = update.message.text

    if chat_id not in user_state:
        reset_user(chat_id)

    state = user_state[chat_id]
    step = state["step"]

    # ---------------- BACK ---------------- #

    if text == "⬅️ Back":

        if step == "DEPARTMENT":
            await start(update, context)
            return

        if step == "YEAR":
            state["step"] = "DEPARTMENT"
            await update.message.reply_text(
                "Choose your department:",
                reply_markup=make_keyboard(DEPARTMENTS, 1)
            )
            return

        if step == "SEMESTER":
            state["step"] = "YEAR"
            await update.message.reply_text(
                "Select your year:",
                reply_markup=make_keyboard(YEARS)
            )
            return

        if step == "STREAM":
            state["step"] = "SEMESTER"
            await update.message.reply_text(
                "Select semester:",
                reply_markup=make_keyboard(SEMESTERS)
            )
            return

        if step == "SUBJECT":
            if state["stream"]:
                state["step"] = "STREAM"
                streams = SOFTWARE_STREAMS if state["department"] == "Software Engineering" else ELECTRICAL_STREAMS
                await update.message.reply_text(
                    "Select your stream:",
                    reply_markup=make_keyboard(streams)
                )
            else:
                state["step"] = "SEMESTER"
                await update.message.reply_text(
                    "Select semester:",
                    reply_markup=make_keyboard(SEMESTERS)
                )
            return

    # ---------------- START ---------------- #

    if step == "START" and text == "START":
        state["step"] = "DEPARTMENT"
        await update.message.reply_text(
            "Choose your department:",
            reply_markup=make_keyboard(DEPARTMENTS, 1)
        )
        return

    # ---------------- DEPARTMENT ---------------- #

    if step == "DEPARTMENT" and text in DEPARTMENTS:
        state["department"] = text
        state["step"] = "YEAR"
        await update.message.reply_text(
            "Select your year:",
            reply_markup=make_keyboard(YEARS)
        )
        return

    # ---------------- YEAR ---------------- #

    if step == "YEAR" and text in YEARS:
        state["year"] = text
        state["step"] = "SEMESTER"
        await update.message.reply_text(
            "Select semester:",
            reply_markup=make_keyboard(SEMESTERS)
        )
        return

    # ---------------- SEMESTER ---------------- #

    if step == "SEMESTER" and text in SEMESTERS:
        state["semester"] = text

        # STREAM CONDITIONS
        if state["department"] == "Software Engineering" and state["year"] in ["4th Year", "5th Year"]:
            state["step"] = "STREAM"
            await update.message.reply_text(
                "Select your stream:",
                reply_markup=make_keyboard(SOFTWARE_STREAMS)
            )
            return

        if (
            state["department"] == "Electrical Engineering"
            and (
                state["year"] == "5th Year"
                or (state["year"] == "4th Year" and text == "2nd Semester")
            )
        ):
            state["step"] = "STREAM"
            await update.message.reply_text(
                "Select your stream:",
                reply_markup=make_keyboard(ELECTRICAL_STREAMS)
            )
            return

        # NO STREAM → SUBJECT
        state["step"] = "SUBJECT"

        subjects = (
            SUBJECTS
            .get(state["department"], {})
            .get(state["year"], {})
            .get(state["semester"], ["Demo Subject"])
        )

        await update.message.reply_text(
            "Choose subject:",
            reply_markup=make_keyboard(subjects, 1)
        )
        return

    # ---------------- STREAM ---------------- #

    if step == "STREAM":

        streams = (
            SOFTWARE_STREAMS
            if state["department"] == "Software Engineering"
            else ELECTRICAL_STREAMS
        )

        if text in streams:
            state["stream"] = text
            state["step"] = "SUBJECT"

            subjects = (
                SUBJECTS
                .get(state["department"], {})
                .get(state["year"], {})
                .get(state["semester"], ["Demo Subject"])
            )

            await update.message.reply_text(
                "Choose subject:",
                reply_markup=make_keyboard(subjects, 1)
            )
            return


    # ---------------- SUBJECT ---------------- #

    if step == "SUBJECT":

        subjects = (
            SUBJECTS
            .get(state["department"], {})
            .get(state["year"], {})
            .get(state["semester"], ["Demo Subject"])
        )

        # User is SELECTING subject
        if text in subjects:
            state["subject"] = text
            state["step"] = "MATERIAL"

            await update.message.reply_text(
                "Choose material type:",
                reply_markup=make_keyboard(MATERIAL_TYPES)
            )
            return

        # Otherwise just SHOW subjects
        await update.message.reply_text(
            "Choose subject:",
            reply_markup=make_keyboard(subjects, 1)
        )
        return


    # ---------------- MATERIAL ---------------- #

    if step == "MATERIAL" and text in MATERIAL_TYPES:
        await update.message.reply_text(
            f"📚 Materials\n\n"
            f"Department: {state['department']}\n"
            f"Year: {state['year']}\n"
            f"Semester: {state['semester']}\n"
            f"Stream: {state['stream']}\n"
            f"Subject: {state['subject']}\n"
            f"Type: {text}",
            reply_markup=ReplyKeyboardMarkup([["START"]], resize_keyboard=True)
        )
        reset_user(chat_id)
        return


# ---------------- MAIN ---------------- #

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    # check if the drive config file exists and it aint empty 
    root_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
    path = Path(DRIVE_CONFIG_PATH)
    NotExistsOrEmpty = not path.exists() or path.stat().st_size == 0
    
    if READ_DRIVE_STATUS:
        print("📂 Drive reading is ENABLED.")
        generate_drive_config(
            root_folder_id=root_folder_id,
            output_path=DRIVE_CONFIG_PATH
            )
        
    elif not READ_DRIVE_STATUS and NotExistsOrEmpty:
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