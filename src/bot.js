import TelegramBot from "node-telegram-bot-api";
import UserState from "./models/UserState.js";
import Material from "./models/Material.js";
import { mkKeyboard } from "./helpers/keyboards.js";
import {
  DEPARTMENTS,
  SOFTWARE_STREAMS,
  ELECTRICAL_STREAMS,
  YEARS,
  SEMESTERS,
  MATERIAL_TYPES
} from "./config/constants.js";
import dotenv from "dotenv";

dotenv.config();

const token = process.env.TELEGRAM_TOKEN;

export default function botInit() {
  const bot = new TelegramBot(token, { polling: true });
//   console.log("Bot started. Token:", token);

  // reset user helper
  async function resetUser(userId) {
    await UserState.findOneAndUpdate(
      { userId },
      { step: "START", department: null, year: null, stream: null, semester: null, subject: null },
      { upsert: true }
    );
  }

  // /start command
  bot.onText(/\/start/, async (msg) => {
    const chatId = msg.chat.id;
    await UserState.findOneAndUpdate({ userId: chatId }, {}, { upsert: true });
    await resetUser(chatId);

    const opts = mkKeyboard([{ text: "START", callback_data: "START" }], 1);
    bot.sendMessage(chatId, "Welcome to 5kilo Academic Material Bot 🎓\nPress START to continue.", opts);
  });

  // handle callbacks
  bot.on("callback_query", async (callbackQuery) => {
    const data = callbackQuery.data;
    const chatId = callbackQuery.from.id;

    let user = await UserState.findOne({ userId: chatId });
    if (!user) user = await UserState.create({ userId: chatId, step: "START" });

    // BACK handler
    if (data === "BACK") {
      switch (user.step) {
        case "START":
        case "DEPARTMENT":
          await resetUser(chatId);
          return bot.editMessageText("Welcome to 5kilo Academic Material Bot 🎓\nPress START to continue.", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard([{ text: "START", callback_data: "START" }], 1)
          });
        case "YEAR":
          await UserState.updateOne({ userId: chatId }, { step: "DEPARTMENT", department: null });
          return bot.editMessageText("Choose your department:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(DEPARTMENTS.map(d => ({ text: d.display, callback_data: d.value })).concat([{ text: "BACK", callback_data: "BACK" }]), 2)
          });
        case "STREAM":
          await UserState.updateOne({ userId: chatId }, { step: "YEAR", stream: null });
          return bot.editMessageText("Select your year:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(YEARS.map(y => ({ text: `${y} Year`, callback_data: `Y_${y}` })).concat([{ text: "BACK", callback_data: "BACK" }]), 2)
          });
        case "SEMESTER":
          if (user.department === "software" || user.department === "electrical") {
            await UserState.updateOne({ userId: chatId }, { step: "STREAM", semester: null });
            const streams = user.department === "software" ? SOFTWARE_STREAMS : ELECTRICAL_STREAMS;
            return bot.editMessageText("Select your stream:", {
              chat_id: chatId,
              message_id: callbackQuery.message.message_id,
              ...mkKeyboard(streams.map(s => ({ text: s.display, callback_data: s.value })).concat([{ text: "BACK", callback_data: "BACK" }]), 2)
            });
          } else {
            await UserState.updateOne({ userId: chatId }, { step: "YEAR", semester: null });
            return bot.editMessageText("Select your year:", {
              chat_id: chatId,
              message_id: callbackQuery.message.message_id,
              ...mkKeyboard(YEARS.map(y => ({ text: `${y} Year`, callback_data: `Y_${y}` })).concat([{ text: "BACK", callback_data: "BACK" }]), 2)
            });
          }
        case "SUBJECT":
          await UserState.updateOne({ userId: chatId }, { step: "SEMESTER", subject: null });
          return bot.editMessageText("Select semester:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(SEMESTERS.map(s => ({ text: `${s} Semester`, callback_data: `S_${s}` })).concat([{ text: "BACK", callback_data: "BACK" }]), 2)
          });
        case "MATERIAL_TYPE":
          await UserState.updateOne({ userId: chatId }, { step: "SUBJECT" });
          const parts = { department: user.department, year: user.year, stream: user.stream, semester: user.semester };
          const subjects = await Material.distinct("subject", parts);
          return bot.editMessageText("Choose subject:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(subjects.map(s => ({ text: s, callback_data: `SUB_${s}` })).concat([{ text: "BACK", callback_data: "BACK" }]), 1)
          });
      }
    }

    // Normal flow
    switch (user.step) {
      case "START":
        if (data === "START") {
          await UserState.updateOne({ userId: chatId }, { step: "DEPARTMENT" });
          return bot.editMessageText("Choose your department:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(DEPARTMENTS.map(d => ({ text: d.display, callback_data: d.value })).concat([{ text: "BACK", callback_data: "BACK" }]), 2)
          });
        }
        break;

      case "DEPARTMENT":
        if (DEPARTMENTS.map(d=>d.value).includes(data)) {
          await UserState.updateOne({ userId: chatId }, { department: data, step: "YEAR" });
          return bot.editMessageText("Select your year:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(YEARS.map(y => ({ text: `${y} Year`, callback_data: `Y_${y}` })).concat([{ text: "BACK", callback_data: "BACK" }]), 2)
          });
        }
        break;

      case "YEAR":
        if (data.startsWith("Y_")) {
          const year = parseInt(data.split("_")[1]);
          await UserState.updateOne({ userId: chatId }, { year });

          // Reload user to check real-time updated year/department
          const updatedUser = await UserState.findOne({ userId: chatId });

          const dep = updatedUser.department;
          const yr = updatedUser.year;

          // 🔥 STREAM CHECK LOGIC
          const needsStream =
            (dep === "software" && (yr === 4 || yr === 5)) ||
            (dep === "electrical" && yr === 5) ||  
            (dep === "electrical" && yr === 4); // temporary check, removed below

          // ❗ FINAL ELECTRICAL STREAM RULE
          // electrical 4th → only second semester requires stream
          if (dep === "electrical" && yr === 4) {
            // DO NOT show stream here — go to semester first
            await UserState.updateOne({ userId: chatId }, { step: "SEMESTER" });
            return bot.editMessageText("Select semester:", {
              chat_id: chatId,
              message_id: callbackQuery.message.message_id,
              ...mkKeyboard(
                SEMESTERS.map(s => ({
                  text: `${s} Semester`,
                  callback_data: `S_${s}`
                })).concat([{ text: "BACK", callback_data: "BACK" }]),
                2
              )
            });
          }

          // For 4th year SW or 5th year SW/EE → stream required immediately
          if (
            (dep === "software" && (yr === 4 || yr === 5)) ||
            (dep === "electrical" && yr === 5)
          ) {
            await UserState.updateOne({ userId: chatId }, { step: "STREAM" });
            const streams =
              dep === "software" ? SOFTWARE_STREAMS : ELECTRICAL_STREAMS;

            return bot.editMessageText("Select your stream:", {
              chat_id: chatId,
              message_id: callbackQuery.message.message_id,
              ...mkKeyboard(
                streams
                  .map(s => ({ text: s.display, callback_data: s.value }))
                  .concat([{ text: "BACK", callback_data: "BACK" }]),
                2
              )
            });
          }

          // Default → go to semester
          await UserState.updateOne({ userId: chatId }, { step: "SEMESTER" });
          return bot.editMessageText("Select semester:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(
              SEMESTERS.map(s => ({
                text: `${s} Semester`,
                callback_data: `S_${s}`
              })).concat([{ text: "BACK", callback_data: "BACK" }]),
              2
            )
          });
        }
        break;
      case "STREAM":
        if (
          SOFTWARE_STREAMS.map(s => s.value)
            .concat(ELECTRICAL_STREAMS.map(s => s.value))
            .includes(data)
        ) {
          await UserState.updateOne(
            { userId: chatId },
            { stream: data, step: "SEMESTER" }
          );

          return bot.editMessageText("Select semester:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(
              SEMESTERS.map(s => ({
                text: `${s} Semester`,
                callback_data: `S_${s}`
              })).concat([{ text: "BACK", callback_data: "BACK" }]),
              2
            )
          });
        }
        break;

      case "SEMESTER":
        if (data.startsWith("S_")) {
          const semester = parseInt(data.split("_")[1]);

          const updated = await UserState.findOne({ userId: chatId });

          // 🔥 Special ELECTRICAL 4th year rule:
          // if 4th year and semester == 2 → NOW show stream
          if (
            updated.department === "electrical" &&
            updated.year === 4 &&
            semester === 2 &&
            !updated.stream // prevent loops
          ) {
            await UserState.updateOne({ userId: chatId }, { step: "STREAM" });

            return bot.editMessageText("Select your stream:", {
              chat_id: chatId,
              message_id: callbackQuery.message.message_id,
              ...mkKeyboard(
                ELECTRICAL_STREAMS.map(s => ({
                  text: s.display,
                  callback_data: s.value
                })).concat([{ text: "BACK", callback_data: "BACK" }]),
                2
              )
            });
          }

          // Otherwise normal flow
          await UserState.updateOne(
            { userId: chatId },
            { step: "SUBJECT", semester }
          );

          const query = {
            department: updated.department.toLowerCase(),
            year: updated.year,
            semester
          };
          if (updated.stream)
            query.stream = updated.stream.toLowerCase();

          const subjects = await Material.distinct("subject", query);

          if (!subjects || subjects.length === 0) {
            return bot.editMessageText("No subjects found. Press BACK.", {
              chat_id: chatId,
              message_id: callbackQuery.message.message_id,
              ...mkKeyboard([{ text: "BACK", callback_data: "BACK" }], 1)
            });
          }

          return bot.editMessageText("Choose subject:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(
              subjects
                .map(s => ({ text: s, callback_data: `SUB_${s}` }))
                .concat([{ text: "BACK", callback_data: "BACK" }]),
              1
            )
          });
        }
        break;


      case "SUBJECT":
        if (data.startsWith("SUB_")) {
          const subject = data.split("_").slice(1).join("_");
          await UserState.updateOne({ userId: chatId, step: "MATERIAL_TYPE", subject });

          return bot.editMessageText("Choose material type:", {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard(MATERIAL_TYPES.map(t => ({ text: t, callback_data: `MT_${t}` })).concat([{ text: "BACK", callback_data: "BACK" }]), 3)
          });
        }
        break;

      case "MATERIAL_TYPE":
        if (data.startsWith("MT_")) {
          const mtype = data.split("_")[1];
          const current = await UserState.findOne({ userId: chatId });

          const query = {
            department: current.department.toLowerCase(),
            year: current.year,
            semester: current.semester,
            subject: current.subject,
            material_type: mtype
          };
          if (current.stream) query.stream = current.stream.toLowerCase();

          const materials = await Material.find(query).limit(20);
          if (!materials || materials.length === 0) {
            return bot.editMessageText("No materials found. Press BACK to try another.", {
              chat_id: chatId,
              message_id: callbackQuery.message.message_id,
              ...mkKeyboard([{ text: "BACK", callback_data: "BACK" }], 1)
            });
          }

          let text = `Materials for ${current.subject} (${mtype}):\n\n`;
          materials.forEach((m, idx) => {
            text += `${idx+1}. ${m.title}\n${m.file_url}\n\n`;
          });

          await bot.editMessageText(text, {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id,
            ...mkKeyboard([
              { text: "Back to Subjects", callback_data: "BACK" },
              { text: "Main Menu", callback_data: "START" }
            ], 2)
          });

          await resetUser(chatId);
        }
        break;
    }

    bot.answerCallbackQuery(callbackQuery.id).catch(() => {});
  });

  bot.on("message", (msg) => {
    const chatId = msg.chat.id;
    if (msg.text && !msg.text.startsWith("/")) {
      bot.sendMessage(chatId, "Use the buttons to navigate. Send /start to begin.");
    }
  });
}
