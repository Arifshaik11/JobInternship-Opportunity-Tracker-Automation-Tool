Job/Internship Opportunity Tracker Automation Tool

📌 Overview:
This tool automates tracking of job/internship opportunities from selected company career portals. It periodically checks for new postings, filters them based on preferences, and sends email notifications.

🚀 Features:
- Automatic scraping of job listings from given URLs.
- Filtering based on keywords or preferences.
- Email notifications for new job postings.
- Uses .env for sensitive credentials (Gmail App Password).

📂 Project Structure:
JOBINTERNSHIP OPPORTUNITY TRACKER AUTOMATION TOOL/
│
├── .env                -> Stores your email & app password (private)
├── job_tracker.py      -> Main script

⚙️ Setup:
1. Clone or copy project to your computer.
2. Install dependencies:
   pip install requests beautifulsoup4 python-dotenv
3. Create a `.env` file in the same folder as job_tracker.py (see example below).
4. Run script:
   python job_tracker.py

📧 Gmail App Password Setup:
1. Go to your Google Account → Security.
2. Enable 2-Step Verification.
3. Create a 16-character App Password for "Mail".
4. Use that password in `.env` under EMAIL_PASS.

📄 Example `.env` file:
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
KEYWORDS=python,developer,internship

(No quotes needed unless your password or keywords contain special characters like # or =.)

🌐 Adding Company URLs:
1. Open `job_tracker.py`.
2. Look for the list named `company_urls` (or similar).
3. Add URLs of the career pages you want to track. Example:
   company_urls = [
       "https://careers.company1.com/jobs",
       "https://company2.com/careers"
   ]
4. Make sure these URLs directly show job listings, not just a generic landing page.
5. If job links in emails are broken, check the scraping code for `a['href']` and ensure it adds the full website domain (e.g., `https://company.com` + relative path).

🛠 Known Issues:
- Job links may be incomplete if the site uses relative URLs — fix by appending the site’s base URL.
- Script may need updates if the career page changes HTML structure.

💡 Tip:
When starting a new ChatGPT session, share this readme.txt with your assistant so they understand your project instantly.

contributor :
arifshaik11