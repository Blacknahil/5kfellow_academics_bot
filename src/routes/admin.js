import express from "express";
import Material from "../models/Material.js";

const router = express.Router();

// use ADMIN_TOKEN in header x-admin-token
router.post("/upload", async (req, res) => {
  try {
    const token = req.headers["x-admin-token"];
    if (token !== process.env.ADMIN_TOKEN) {
      return res.status(401).json({ message: "unauthorized" });
    }

    const { title, file_url, material_type, department, year, stream, semester, subject } = req.body;

    const m = new Material({ title, file_url, material_type, department, year, stream, semester, subject });
    await m.save();
    res.json({ message: "ok", material: m });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "error", error: err.message });
  }
});

export default router;
