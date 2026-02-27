from constants import (
    DEPARTMENTS,
    SOFTWARE_STREAMS,
    ELECTRICAL_STREAMS,
    YEARS,
    SEMESTERS,
    MATERIAL_TYPES,
)
from utils import make_keyboard, get_files


async def handle_start_step(update, context, state, text):
    state["step"] = "DEPARTMENT"
    await update.message.reply_text(
        "Choose your department:",
        reply_markup=make_keyboard(DEPARTMENTS)
    )

async def handle_department_step(update, context, state, text):
    # RENDER MODE (Back navigation)
    if text == "back":
        await update.message.reply_text(
            "Choose your department:",
            reply_markup=make_keyboard(DEPARTMENTS)
        )
        return
    # INPUT MODE (Moving forward)
    if text not in DEPARTMENTS:
        return

    state["department"] = text
    state["step"] = "YEAR"

    await update.message.reply_text(
        "Select your year:",
        reply_markup=make_keyboard(YEARS)
    )


async def handle_year_step(update, context, state, text):
    
    # RENDER MODE (Back navigation)
    if text == "back":
        await update.message.reply_text(
            "Select your year:",
            reply_markup=make_keyboard(YEARS)
        )
        return
    
    #INPUT MODE(Moving forward)
    if text not in YEARS:
        return

    state["year"] = text
    state["step"] = "SEMESTER"

    await update.message.reply_text(
        "Select semester:",
        reply_markup=make_keyboard(SEMESTERS)
    )

async def handle_semester_step(update, context, state, text):
    # RENDER MODE (Back navigation)
    if text == "back":
        await update.message.reply_text(
            "Select semester:",
            reply_markup=make_keyboard(SEMESTERS)
        )
        return
    
    # INPUT MODE (Moving forward)
    if text not in SEMESTERS:
        return
    state["semester"] = text

    # Stream conditions
    if state["department"] == "Software" and state["year"] in ["Fourth Year", "Fifth Year"]:
        state["step"] = "STREAM"
        await update.message.reply_text(
            "Select your stream:",
            reply_markup=make_keyboard(SOFTWARE_STREAMS)
        )
        return

    if (
        state["department"] == "Electrical"
        and (
            state["year"] == "Fifth Year"
            or (state["year"] == "Fourth Year" and text == "Second Semester")
        )
    ):
        state["step"] = "STREAM"
        await update.message.reply_text(
            "Select your stream:",
            reply_markup=make_keyboard(ELECTRICAL_STREAMS)
        )
        return

    # No stream → subject
    await enter_subject_step(update, context, state)

async def handle_stream_step(update, context, state, text):
    
    # RENDER MODE (Back navigation)
    if text == "back":
        streams = SOFTWARE_STREAMS if state["department"] == "Software" else ELECTRICAL_STREAMS
        await update.message.reply_text(
            "Select your stream:",
            reply_markup=make_keyboard(streams)
        )
        return
    
    # INPUT MODE (Moving forward)
    streams = SOFTWARE_STREAMS if state["department"] == "Software" else ELECTRICAL_STREAMS

    if text not in streams:
        return

    state["stream"] = text
    await enter_subject_step(update, context,state)


async def enter_subject_step(update, context, state):
    '''
    handles getting the list of the courses in the specified department, year, semeseter, stream  and 
    passes it on to the handle_subject_step by saving the courses list in state[subjects]'''
    
    config_map = context.bot_data["config_map"]
    try:
        department = state["department"].lower().replace(" ", "_") if state["department"] else ""
        year = state["year"].lower().replace(" ", "_") if state["year"] else ""
        stream = state.get("stream", "").lower().replace(" ", "_") if state.get("stream") else ""
        semester = state["semester"].lower().replace(" ", "_") if state["semester"] else ""
        
        print("querying subjects for:", department, year, semester, stream)
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
        "Select your Course:",
        reply_markup=make_keyboard(subjects)
    )

async def handle_subject_step(update, context, state, text):
    # RENDER MODE (Back navigation)
    if text == "back":
        subjects = state["subjects"]
        await update.message.reply_text(
            "Please choose your Course:",
            reply_markup = make_keyboard(subjects)
        )
        return 
     # INPUT MODE (Moving forward)
    subjects = state["subjects"]
    
    if text is None:
        await update.message.reply_text(
            "Select your Course:",
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
        reply_markup=make_keyboard(MATERIAL_TYPES)
    )

async def handle_material_step(update, context, state, text):

    if text == "back":
        await update.message.reply_text(
            "Choose material type:",
            reply_markup=make_keyboard(MATERIAL_TYPES)
    )
        return
    
    if text not in MATERIAL_TYPES:
        await update.message.reply_text(
            "Please choose a valid Material type:"
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
            text,
            config_map
        )
    except KeyError:
        await update.message.reply_text("No files found.")
        return

    state["step"] = "FILE_SELECTION"
    state["material_type"] = text
    state["files"] = files

    msg = ""
    file_names = []

    if len(files) == 0:
        msg = f"No {text} found"
        
    else:
        msg = f"📁 Available {text}:"
        for fname in files:
            print("file found: ", fname)
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
        print("File sent successfully.")
    else:
        await update.message.reply_text("Failed to send file.")
    
