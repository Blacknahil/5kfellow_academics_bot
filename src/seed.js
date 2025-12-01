import mongoose from "mongoose";
import dotenv from "dotenv";
import Material from "./models/Material.js";

dotenv.config();

async function seed() {
  try {
    await mongoose.connect(process.env.MONGODB_URI);
    console.log("DB connected");

    await Material.create({
      department: "software",
      year: "2",
      semester: "1",
      stream: "", 
      subject: "Data Structures",
      type: "slide",
      link: "https://drive.google.com/test-datastructures-slides"
    });

    await Material.create({
      department: "software",
      year: "2",
      semester: "1",
      stream: "",
      subject: "Data Structures",
      type: "book",
      link: "https://drive.google.com/test-datastructures-book"
    });

    await Material.create({
      department: "software",
      year: "2",
      semester: "1",
      stream: "",
      subject: "Data Structures",
      type: "exam",
      link: "https://drive.google.com/test-datastructures-exam"
    });

    console.log("Mock data added successfully");
    process.exit(0);

  } catch (err) {
    console.error(err);
    process.exit(1);
  }
}

seed();
