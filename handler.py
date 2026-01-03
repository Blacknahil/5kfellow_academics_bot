from constants import (
    DEPARTMENTS,
    SOFTWARE_STREAMS,
    ELECTRICAL_STREAMS,
    YEARS,
    SEMESTERS,
    MATERIAL_TYPES,
    SUBJECTS
)
from utils import make_keyboard, get_files


async def handle_start_step(update, state):
    state["step"] = "DEPARTMENT"
    await update.message.reply_text(
        "Choose your department:",
        reply_markup=make_keyboard(DEPARTMENTS, 1)
    )

async def handle_department_step(update, state, text):
    if text not in DEPARTMENTS:
        return

    state["department"] = text
    state["step"] = "YEAR"

    await update.message.reply_text(
        "Select your year:",
        reply_markup=make_keyboard(YEARS)
    )


async def handle_year_step(update, state, text):
    if text not in YEARS:
        return

    state["year"] = text
    state["step"] = "SEMESTER"

    await update.message.reply_text(
        "Select semester:",
        reply_markup=make_keyboard(SEMESTERS)
    )

async def handle_semester_step(update, state, text):
    if text not in SEMESTERS:
        return

    state["semester"] = text

    # Stream conditions
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

    # No stream → subject
    await enter_subject_step(update, state)

async def handle_stream_step(update, state, text):
    streams = SOFTWARE_STREAMS if state["department"] == "Software Engineering" else ELECTRICAL_STREAMS

    if text not in streams:
        return

    state["stream"] = text
    await enter_subject_step(update, state)


async def enter_subject_step(update, state):
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

async def handle_subject_step(update, state, text):
    subjects = (
        SUBJECTS
        .get(state["department"], {})
        .get(state["year"], {})
        .get(state["semester"], ["Demo Subject"])
    )

    if text not in subjects:
        return

    state["subject"] = text
    state["step"] = "MATERIAL"

    await update.message.reply_text(
        "Choose material type:",
        reply_markup=make_keyboard(MATERIAL_TYPES)
    )

async def handle_material_step(update, context, state, text):
    if text not in MATERIAL_TYPES:
        return

    config_map = context.bot_data["config_map"]

    try:
        files = get_files(
            state["department"],
            state["year"],
            state["semester"],
            state.get("stream"),
            state["subject"],
            text,
            config_map
        )
    except KeyError:
        await update.message.reply_text("No files found.")
        return

    state["step"] = "FILE_SELECTION"
    state["material_type"] = text
    state["files"] = files

    msg = f"📁 Available {text}:\n\n"
    for i, f in enumerate(files, 1):
        msg += f"{i}. {f['name']}\n"

    msg += "\nSend the number of the file you want."
    await update.message.reply_text(msg)

async def handle_file_selection_step(update, context, state, text):
    if not text.isdigit():
        await update.message.reply_text("Send a valid number.")
        return

    idx = int(text) - 1
    files = state["files"]

    if idx < 0 or idx >= len(files):
        await update.message.reply_text("Invalid number.")
        return

    drive_id = files[idx]["drive_id"]
    file_manager = context.bot_data["file_manager"]

    await update.message.reply_text("📥 Fetching file...")
    await file_manager.send_file(update, context, drive_id)
    
    
    
