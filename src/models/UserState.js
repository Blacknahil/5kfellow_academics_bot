import mongoose from "mongoose";

const UserStateSchema = new mongoose.Schema({
  userId: { type: Number, required: true, unique: true },
  step: { type: String, default: "START" }, // START, DEPARTMENT, YEAR, STREAM, SEMESTER, SUBJECT, MATERIAL_TYPE
  department: { type: String, default: null },
  year: { type: Number, default: null },
  stream: { type: String, default: null },
  semester: { type: Number, default: null },
  subject: { type: String, default: null }
});

export default mongoose.model("UserState", UserStateSchema);
