from telegram.ext import ContextTypes
from telegram import Update

from constants import (
    DEPARTMENTS,
    SOFTWARE_STREAMS,
    ELECTRICAL_STREAMS,
    YEARS,
    SEMESTERS,
    MATERIAL_TYPES,
)

from utils import make_keyboard, get_files, extract_book_club_files
from analytics.tracker import track_download,track_failed
from analytics.tracker import get_stats


async def handle_start_step(update, context, state, text):
    state["step"] = "DEPARTMENT"
    await update.message.reply_text(
        "Choose your department:",
        reply_markup=make_keyboard(DEPARTMENTS.keys())
    )
    
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats()
    msg = (
        "📊 Bot Statistics\n\n"
        f"👤 Total Users: {stats['total_users']}\n"
        f"🆕 Users Today: {stats['users_today']}\n"
        f"📨 Requests Today: {stats['requests_today']}\n"
        f"📦 Total Requests: {stats['total_requests']}\n"
        f"📥 Downloads Today: {stats['downloads_today']}\n"
        f"📚 Total Downloads: {stats['total_downloads']}\n"
        f"❌ Failed Downloads Today: {stats['failed_today']}\n\n"
        f"🏆 Most Active Department: {stats['top_department']}\n"
    )
    await update.message.reply_text(msg)

async def handle_department_step(update, context, state, text):
    # RENDER MODE (Back navigation)
    if text == "back":
        await update.message.reply_text(
            "Choose your department:",
            reply_markup=make_keyboard(DEPARTMENTS.keys())
        )
        return
    # INPUT MODE (Moving forward)
    if text not in DEPARTMENTS:
        return

    state["department"] = DEPARTMENTS[text]

    if state["department"] == "book_club":
        await enter_book_club_step(update, context, state)
        return

    state["step"] = "YEAR"

    await update.message.reply_text(
        "Select your year:",
        reply_markup=make_keyboard(YEARS.keys())
    )

async def enter_book_club_step(update, context, state):
    config_map = context.bot_data["config_map"]
    files = extract_book_club_files(config_map)

    if not files:
        await update.message.reply_text("No books found.")
        return

    state["step"] = "FILE_SELECTION"
    state["material_type"] = "books"
    state["files"] = files

    await update.message.reply_text(
        "Book Club Recommendations:",
        reply_markup=make_keyboard(files.keys(), back=True)
    )


async def handle_year_step(update, context, state, text):
    
    # RENDER MODE (Back navigation)
    if text == "back":
        await update.message.reply_text(
            "Select your year:",
            reply_markup=make_keyboard(YEARS.keys())
        )
        return
    
    #INPUT MODE(Moving forward)
    if text not in YEARS:
        return

    state["year"] = YEARS[text]
    state["step"] = "SEMESTER"

    await update.message.reply_text(
        "Select semester:",
        reply_markup=make_keyboard(SEMESTERS.keys())
    )

async def handle_semester_step(update, context, state, text):
    # RENDER MODE (Back navigation)
    if text == "back":
        await update.message.reply_text(
            "Select semester:",
            reply_markup=make_keyboard(SEMESTERS.keys())
        )
        return
    
    # INPUT MODE (Moving forward)
    if text not in SEMESTERS:
        return
    state["semester"] = SEMESTERS[text]

    # Stream conditions
    if state["department"] == "software" and state["year"] in ["fourth_year", "fifth_year"]:
        state["step"] = "STREAM"
        await update.message.reply_text(
            "Select your stream:",
            reply_markup=make_keyboard(SOFTWARE_STREAMS.keys())
        )
        return

    if (
        state["department"] == "electrical"
        and (
            state["year"] == "fifth_year"
            or (state["year"] == "fourth_year" and SEMESTERS.get(text) == "second_semester")
        )
    ):
        state["step"] = "STREAM"
        await update.message.reply_text(
            "Select your stream:",
            reply_markup=make_keyboard(ELECTRICAL_STREAMS.keys())
        )
        return

    # No stream → subject
    await enter_subject_step(update, context, state)

async def handle_stream_step(update, context, state, text):
    
    # RENDER MODE (Back navigation)
    if text == "back":
        streams = SOFTWARE_STREAMS if state["department"] == "software" else ELECTRICAL_STREAMS
        await update.message.reply_text(
            "Select your stream:",
            reply_markup=make_keyboard(streams.keys())
        )
        return
    
    # INPUT MODE (Moving forward)
    streams = SOFTWARE_STREAMS if state["department"] == "software" else ELECTRICAL_STREAMS

    if text not in streams:
        return

    state["stream"] = streams[text]
    await enter_subject_step(update, context,state)


async def enter_subject_step(update, context, state):
    '''
    handles getting the list of the courses in the specified department, year, semeseter, stream  and 
    passes it on to the handle_subject_step by saving the courses list in state[subjects]'''
    
    config_map = context.bot_data["config_map"]
    try:
        department = state["department"] if state["department"] else ""
        year = state["year"] if state["year"] else ""
        stream = state.get("stream", "") if state.get("stream") else ""
        semester = state["semester"] if state["semester"] else ""
        
        node = (
            config_map
            .get(department, {})
            .get(year, {})
            .get(semester, {})
        )
        if stream:
            node = node.get(stream, {})
        subjects = list(node.keys())
        
    except KeyError:
        await update.message.reply_text("No Courses found.")
        return 
    
    if not subjects:
        await update.message.reply_text("No Courses found.")
        return
    state["step"] = "SUBJECT"
    state["subjects"] = subjects
    
    await update.message.reply_text(
        "Select your course:",
        reply_markup=make_keyboard(subjects)
    )

async def handle_subject_step(update, context, state, text):
    # RENDER MODE (Back navigation)
    if text == "back":
        subjects = state["subjects"]
        await update.message.reply_text(
            "Select your course:",
            reply_markup = make_keyboard(subjects)
        )
        return 
     # INPUT MODE (Moving forward)
    subjects = state["subjects"]
    
    if text is None:
        await update.message.reply_text(
            "Select your course:",
            reply_markup=make_keyboard(subjects)
        )
        return

    if text not in subjects:
        await update.message.reply_text(
            "Please choose a valid course: ")
        return
    
    state["subject"] = text
    state["step"] = "MATERIAL"

    await update.message.reply_text(
        "Choose material type:",
        reply_markup=make_keyboard(MATERIAL_TYPES.keys())
    )

async def handle_material_step(update, context, state, text):

    if text == "back":
        await update.message.reply_text(
            "Choose material type:",
            reply_markup=make_keyboard(MATERIAL_TYPES.keys())
    )
        return
    
    if text not in MATERIAL_TYPES:
        await update.message.reply_text(
            "Please choose a valid material type:"
        )
        return


    config_map = context.bot_data["config_map"]

    try:
        files = get_files(
            state["department"],
            state["year"],
            state["semester"],
            state.get("stream"),
            state["subject"],
            MATERIAL_TYPES[text],
            config_map
        )
    except KeyError:
        await update.message.reply_text(f"No {text} found.")
        return

    file_names = []

    if len(files) == 0:
        await update.message.reply_text(msg)
        return 
    
    state["step"] = "FILE_SELECTION"
    state["material_type"] = MATERIAL_TYPES[text]
    state["files"] = files
    
    msg = f"📁 Available {text}:"
    for fname in files:
        file_names.append(fname)
    # await update.message.reply_text()
    await update.message.reply_text(
        msg,
        reply_markup=make_keyboard(file_names,back=True)
    )

async def handle_file_selection_step(update, context, state, text):
    files = state["files"]
    if not text or text not in files:
        await update.message.reply_text("Please use a correct file name")
        return

    drive_id = files[text].drive_id
    file_manager = context.bot_data["file_manager"]

    await update.message.reply_text("📥 Fetching file...")
    chat_id = update.effective_chat.id
    file_sent = await file_manager.get_file(chat_id, drive_id)
    if file_sent.status:
        track_download(state["department"])
    else:
        track_failed()
        await update.message.reply_text("Failed to send file.")
    
