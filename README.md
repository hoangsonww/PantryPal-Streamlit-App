# PantryPal – AI Recipe Generator 🥕

PantryPal is a Streamlit web app that turns the ingredients you have on hand (plus any dietary restrictions) into chef-worthy recipes in seconds. Powered by Google’s Gemini AI and Unsplash for hero images, PantryPal features:

- **Pantry-based recipe generation**  
- **“Surprise Me!”** to let the AI invent a random dish  
- **Dietary restrictions** support (Vegan, Gluten-Free, Halal, etc.)  
- **Servings slider** (1–12 portions)  
- **Hero image selection** for each recipe  
- **Interactive ingredients checklist** & **shopping list** download (TXT)  
- **Nutrition bar & donut charts** per serving  
- **Estimated difficulty** indicator  
- **Persistent recipe history** with delete capability  
- **Download recipe** as JSON, Markdown, or plain TXT  

<p align="center">
  <img src="https://img.shields.io/badge/Python-%3E%3D3.9-3776AB?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-v1.44.1-FE4A49?style=for-the-badge&logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Google%20GenAI-Gemini-blue?style=for-the-badge&logo=google" alt="Google Gemini AI">
  <img src="https://img.shields.io/badge/Unsplash-API-0052CC?style=for-the-badge&logo=unsplash" alt="Unsplash API">
  <img src="https://img.shields.io/badge/python--dotenv-latest-212121?style=for-the-badge&logo=dotenv" alt="python-dotenv">
  <img src="https://img.shields.io/badge/pandas-latest-150458?style=for-the-badge&logo=pandas" alt="pandas">
  <img src="https://img.shields.io/badge/Altair-latest-F47721?style=for-the-badge&logo=altair" alt="Altair">
  <img src="https://img.shields.io/badge/Black-23.7.0-000000?style=for-the-badge" alt="Black">
  <img src="https://img.shields.io/badge/isort-5.12.0-007ACC?style=for-the-badge" alt="isort">
  <img src="https://img.shields.io/badge/License-MIT-4E9F3D?style=for-the-badge&logo=github" alt="MIT License">
</p>

## 🌐 Live App

Try it now in your browser: **[https://pantrypal-app.streamlit.app](https://pantrypal-app.streamlit.app)**. Feel free to explore and generate recipes with your pantry items!

## 🛠️ Prerequisites

- Python 3.9 or later  
- A Google Cloud API key with access to the Generative AI (Gemini) API  
- An Unsplash developer access key for fetching food images  

## 🚀 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/hoangsonww/PantryPal-Streamlit-App.git
   cd PantryPal-Streamlit-App
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # for macOS/Linux
   .venv\Scripts\activate         # for Windows PowerShell
   ```

3. **Install dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## 🔑 Configuration

Create a file named `.env` in the project root with the following variables:

```ini
# .env
GOOGLE_AI_API_KEY=<YOUR_GOOGLE_GEMINI_API_KEY>
UNSPLASH_ACCESS_KEY=<YOUR_UNSPLASH_ACCESS_KEY>
```

- **GOOGLE_AI_API_KEY**: Your Google Cloud API key for the Generative AI (Gemini) API.  
- **UNSPLASH_ACCESS_KEY**: Your Unsplash Access Key (register at https://unsplash.com/developers).


## 📂 Directory Structure

```
pantrypal/
├── app.py
├── components/
│   ├── inputs.py        # Sidebar input UI
│   └── display.py       # Recipe & history rendering
├── utils/
│   ├── genai_client.py  # Gemini AI wrapper
│   ├── image_fetcher.py # Unsplash image fetcher
│   └── storage.py       # JSON‐file storage for history
├── requirements.txt     # Python dependencies
├── recipe_history.json  # Persistent recipe history
└── README.md            # This file
```

## ▶️ Running the App

With your virtual environment active and `.env` configured, simply run:

```bash
streamlit run app.py
```

Then open the URL shown in your terminal (e.g. `http://localhost:8501`) in your browser.

## 🧑‍🍳 How to Use

1. **Enter Ingredients**  
   - Paste a comma-separated list of pantry items (e.g. `chicken, rice, tomato`).  
2. **Select Dietary Restrictions** (optional)  
   - Choose from Vegetarian, Vegan, Gluten-Free, Dairy-Free, etc.  
3. **Adjust Servings**  
   - Slide to set portions (1–12).  
4. **Generate**  
   - Click **Generate Recipe** to fetch from Gemini AI.  
5. **Pick a Hero Image**  
   - If images are available, select your favorite and click **Confirm Image** once.  
6. **View Recipe**  
   - See the title, image, ingredients checklist, shopping list, nutrition charts, difficulty, instructions, and substitutions.  
7. **Download**  
   - Grab the recipe as JSON, Markdown, or plain TXT; download your shopping list (TXT).  
8. **History**  
   - Scroll down to revisit past recipes; use **Delete** to remove any entry.  
9. **Surprise Me!**  
   - Click to have Gemini invent a random recipe from scratch (no pantry required).  
10. **Clear History**  
    - Wipe all saved recipes with one click.  

## ⚙️ Customization

- **Max output tokens** & **temperature** for AI calls can be adjusted in `utils/genai_client.py`.  
- **Caching** for images is handled in `utils/image_fetcher.py` (TTL = 1 hour).  
- **History storage** uses a simple JSON file (`recipe_history.json`) in the project root.  

> For now, the app uses a JSON file for history storage. Future versions may include a database option (e.g., SQLite, PostgreSQL) for better scalability and performance.

## 🤝 Contributing

1. Fork the repo  
2. Create a new branch (`git checkout -b feature/foo`)  
3. Commit your changes (`git commit -m "Add foo"`)  
4. Push to the branch (`git push origin feature/foo`)  
5. Open a Pull Request  

## 📄 License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## 📧 Contact

- [Son Nguyen](https://github.com/hoangsonww)

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework  
- [Google Gemini AI](https://cloud.google.com/generative-ai) for recipe generation  
- [Unsplash](https://unsplash.com/) for beautiful images  
- [Altair](https://altair-viz.github.io/) for interactive charts  
- [Python-dotenv](https://pypi.org/project/python-dotenv/) for environment variable management  
- [pandas](https://pandas.pydata.org/) for data manipulation  

---

Thank you for checking out PantryPal! We hope it makes your cooking adventures easier and more fun. If you have any questions or suggestions, feel free to reach out!  
