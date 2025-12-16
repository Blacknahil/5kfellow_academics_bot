# constants.py

# ---------------- DEPARTMENTS ---------------- #

DEPARTMENTS = [
    "Software Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Biomedical Engineering"
]

# ---------------- STREAMS ---------------- #

SOFTWARE_STREAMS = ["AI", "Software", "IT", "Cyber"]
ELECTRICAL_STREAMS = ["Power", "Computer", "Communication", "Control"]

# ---------------- YEARS & SEMESTERS ---------------- #

YEARS = ["2nd Year", "3rd Year", "4th Year", "5th Year"]
SEMESTERS = ["1st Semester", "2nd Semester"]

# ---------------- MATERIAL TYPES ---------------- #

MATERIAL_TYPES = ["Books", "Slides", "Exams"]

# ---------------- SUBJECTS ---------------- #
# SUBJECTS[department][year][semester]

SUBJECTS = {

    # ==========================================================
    # SOFTWARE ENGINEERING
    # ==========================================================

    "Software Engineering": {
        "2nd Year": {
            "1st Semester": [
                "Applied Mathematics II",
                "Object Oriented Programming",
                "Discrete Mathematics",
                "Engineering Mechanics",
                "Engineering Drawing",
                "Probability and Statistics"
            ],
            "2nd Semester": [
                "Data Structures and Algorithms",
                "Database Systems",
                "Digital Logic Design",
                "Linear Algebra",
                "Entrepreneurship"
            ]
        },

        "3rd Year": {
            "1st Semester": [
                "Web Development",
                "Fundamentals of Software Engineering",
                "Human Computer Interaction",
                "Computer Architecture"
            ],
            "2nd Semester": [
                "Operating Systems",
                "Computer Networks",
                "Software Testing",
                "Numerical Methods"
            ]
        },

        "4th Year": {
            "1st Semester": [
                "Artificial Intelligence",
                "Mobile Application Development",
                "Compiler Design",
                "Distributed Systems"
            ],
            "2nd Semester": [
                "Machine Learning",
                "Cloud Computing",
                "Software Project Management",
                "Research Methods"
            ]
        },

        "5th Year": {
            "1st Semester": [
                "Advanced AI Systems",
                "Big Data Analytics",
                "Secure Software Systems"
            ],
            "2nd Semester": [
                "Final Year Project",
                "Professional Ethics",
                "Startup and Innovation"
            ]
        }
    },

    # ==========================================================
    # ELECTRICAL ENGINEERING
    # ==========================================================

    "Electrical Engineering": {
        "2nd Year": {
            "1st Semester": [
                "Circuit Theory I",
                "Engineering Mathematics II",
                "Electrical Measurements",
                "Programming for Engineers"
            ],
            "2nd Semester": [
                "Circuit Theory II",
                "Electromagnetic Fields",
                "Probability and Statistics"
            ]
        },

        "3rd Year": {
            "1st Semester": [
                "Signals and Systems",
                "Analog Electronics",
                "Electrical Machines I"
            ],
            "2nd Semester": [
                "Digital Electronics",
                "Electrical Machines II",
                "Power Electronics"
            ]
        },

        "4th Year": {
            "1st Semester": [
                "Control Systems",
                "Microprocessors",
                "Communication Systems I"
            ],
            "2nd Semester": [
                "Power Systems I",
                "Communication Systems II",
                "Instrumentation"
            ]
        },

        "5th Year": {
            "1st Semester": [
                "Power Systems II",
                "Advanced Control Systems",
                "Renewable Energy Systems"
            ],
            "2nd Semester": [
                "Industrial Automation",
                "Final Year Project"
            ]
        }
    },

    # ==========================================================
    # MECHANICAL ENGINEERING
    # ==========================================================

    "Mechanical Engineering": {
        "2nd Year": {
            "1st Semester": [
                "Engineering Mechanics",
                "Material Science",
                "Thermodynamics I"
            ],
            "2nd Semester": [
                "Thermodynamics II",
                "Manufacturing Processes",
                "Engineering Mathematics"
            ]
        },

        "3rd Year": {
            "1st Semester": [
                "Fluid Mechanics",
                "Machine Design I",
                "Heat Transfer"
            ],
            "2nd Semester": [
                "Machine Design II",
                "Dynamics of Machinery",
                "Numerical Methods"
            ]
        },

        "4th Year": {
            "1st Semester": [
                "Automobile Engineering",
                "Refrigeration and Air Conditioning"
            ],
            "2nd Semester": [
                "Industrial Engineering",
                "Finite Element Methods"
            ]
        },

        "5th Year": {
            "1st Semester": [
                "Robotics and Automation",
                "Renewable Energy Systems"
            ],
            "2nd Semester": [
                "Final Year Project",
                "Engineering Ethics"
            ]
        }
    },

    # ==========================================================
    # CIVIL ENGINEERING
    # ==========================================================

    "Civil Engineering": {
        "2nd Year": {
            "1st Semester": [
                "Engineering Surveying",
                "Strength of Materials",
                "Engineering Geology"
            ],
            "2nd Semester": [
                "Structural Analysis I",
                "Fluid Mechanics",
                "Probability and Statistics"
            ]
        },

        "3rd Year": {
            "1st Semester": [
                "Structural Analysis II",
                "Geotechnical Engineering I",
                "Transportation Engineering"
            ],
            "2nd Semester": [
                "Geotechnical Engineering II",
                "Hydrology",
                "Environmental Engineering I"
            ]
        },

        "4th Year": {
            "1st Semester": [
                "Reinforced Concrete Design I",
                "Construction Planning"
            ],
            "2nd Semester": [
                "Steel Structure Design",
                "Environmental Engineering II"
            ]
        },

        "5th Year": {
            "1st Semester": [
                "Advanced Structural Design",
                "Project Management"
            ],
            "2nd Semester": [
                "Final Year Project",
                "Professional Practice"
            ]
        }
    },

    # ==========================================================
    # CHEMICAL ENGINEERING
    # ==========================================================

    "Chemical Engineering": {
        "2nd Year": {
            "1st Semester": [
                "Material and Energy Balances",
                "Physical Chemistry"
            ],
            "2nd Semester": [
                "Chemical Engineering Thermodynamics",
                "Fluid Flow Operations"
            ]
        },

        "3rd Year": {
            "1st Semester": [
                "Heat and Mass Transfer",
                "Chemical Reaction Engineering"
            ],
            "2nd Semester": [
                "Separation Processes",
                "Process Control"
            ]
        },

        "4th Year": {
            "1st Semester": [
                "Process Design",
                "Polymer Engineering"
            ],
            "2nd Semester": [
                "Biochemical Engineering",
                "Environmental Engineering"
            ]
        },

        "5th Year": {
            "1st Semester": [
                "Advanced Process Control",
                "Industrial Safety"
            ],
            "2nd Semester": [
                "Final Year Project"
            ]
        }
    },

    # ==========================================================
    # BIOMEDICAL ENGINEERING
    # ==========================================================

    "Biomedical Engineering": {
        "2nd Year": {
            "1st Semester": [
                "Human Anatomy",
                "Medical Physics"
            ],
            "2nd Semester": [
                "Physiology",
                "Biomedical Materials"
            ]
        },

        "3rd Year": {
            "1st Semester": [
                "Biomedical Instrumentation",
                "Signals in Medicine"
            ],
            "2nd Semester": [
                "Medical Imaging Systems",
                "Biostatistics"
            ]
        },

        "4th Year": {
            "1st Semester": [
                "Clinical Engineering",
                "Biomechanics"
            ],
            "2nd Semester": [
                "Rehabilitation Engineering",
                "Healthcare Technology"
            ]
        },

        "5th Year": {
            "1st Semester": [
                "Advanced Medical Devices",
                "Health Informatics"
            ],
            "2nd Semester": [
                "Final Year Project",
                "Biomedical Ethics"
            ]
        }
    }
}
