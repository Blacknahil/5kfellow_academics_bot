## Here are the steps to run the bot
1. Create and activate a virtual environment:
   - `python -m venv venv`
   - `source venv/bin/activate`   (Linux/Mac)
   - `venv\Scripts\activate`      (Windows)
2. Install the dependencies:
   - `pip install -r requirements.txt`
3. Set the required environment variables and Google credentials, for example:
   - `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-credentials.json`  (Linux/Mac)
   - `set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\google-credentials.json`  (Windows)
   - Set any other environment variables required by the bot (API keys, configuration, etc.).
4. Run the bot:
   - `python bot.py`