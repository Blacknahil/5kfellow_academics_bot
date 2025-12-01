import mongoose from "mongoose";

const MaterialSchema = new mongoose.Schema({
  title: { type: String, required: true },
  file_url: { type: String, required: true }, // google drive share link or direct link
  material_type: { type: String, enum: ["book", "slides", "exam"], required: true },
  department: { type: String, required: true }, // e.g., software, electrical, mechanical
  year: { type: Number, required: true }, // 2,3,4,5
  stream: { type: String, default: null }, // optional for streams
  semester: { type: Number, enum: [1,2], required: true },
  subject: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model("Material", MaterialSchema);
