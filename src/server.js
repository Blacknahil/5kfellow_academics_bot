import express from "express";
import mongoose from "mongoose";
import dotenv from "dotenv";
import cors from "cors";
import adminRoutes from "./routes/admin.js";
import botInit from "./bot.js";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Routes
app.use("/admin", adminRoutes);

const PORT = process.env.PORT || 5000;

// Debug
console.log("Connecting to MongoDB...", process.env.MONGODB_URI);

mongoose.connect(process.env.MONGODB_URI)
  .then(() => {
    console.log("Mongo connected");
    app.listen(PORT, () => console.log("Server running on port", PORT));
    botInit();
  })
  .catch(err => {
    console.error("Mongo connection error", err);
  });
