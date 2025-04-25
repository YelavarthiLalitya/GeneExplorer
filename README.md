# Aminoverse — Explore the Universe of Human Proteins

**Aminoverse** is a smart, web-based application that allows users to search for human genes or proteins and explore their biological functions, associated diseases, 3D structures, and protein-protein interactions — all in one place.

---

##  Features

- **Gene/Protein Search** — Search any human gene (e.g., TP53, BRCA1).
- **Biological Function** — View a brief description of the gene's biological role.
- **3D Protein Structure** — Direct link to UniProt’s 3D structure visualization.
- **Protein–Protein Interactions** — Graph of interacting partners using STRING.
- **(Optional)** AI-powered chatbot for follow-up queries.

---

## Tech Stack

| Layer       | Technologies                  |
|-------------|-------------------------------|
| Frontend    | HTML, CSS, Vanilla JavaScript |
| Backend     | Python, Flask                 |
| APIs Used   | UniProt, STRING-DB, DisGeNET  |

---

## Setup Instructions

1. **Clone the repository**
   git clone https://github.com/yourusername/aminoverse.git
   cd aminoverse
2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install dependencies
pip install -r requirements.txt


4. Run the Flask server
python run.py
Open your browser

Go to http://localhost:5000
