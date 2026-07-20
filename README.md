# Python Development Internship Projects

A collection of Python automation scripts built as part of a development
internship — covering web scraping, CLI tooling with regex, and automated
email workflows.

## Projects

| # | Project | Tech Stack |
|---|---------|-----------|
| 1 | [Automated Web Scraper for Property Listings](./task1-web-scraper) | Python, BeautifulSoup4, Requests, csv |
| 2 | [CLI Log Parser for Tour Enquiries](./task2-log-parser) | Python, argparse, re |
| 3 | [Automated Email Notification System](./task3-email-notifier) | Python, smtplib, email.mime, python-dotenv |

---

### 1. Automated Web Scraper for Property Listings
Scrapes property titles, prices, and locations from real estate listing
pages, cleans the extracted data (normalizes prices, strips whitespace,
fills missing values, removes duplicates), and exports it to a formatted
CSV file.

```bash
cd task1-web-scraper
pip install -r requirements.txt
python3 property_scraper.py
```

### 2. CLI Log Parser for Tour Enquiries
A command-line tool that parses messy, unstructured tour-enquiry logs and
extracts names, emails, and destinations using regex, printing a clean
summary table to the terminal.

```bash
cd task2-log-parser
python3 log_parser.py sample_enquiries.txt
python3 log_parser.py sample_enquiries.txt --export results.csv
```

### 3. Automated Email Notification System
Reads a customer list (name, email) from CSV and sends personalized
booking-confirmation emails via Gmail SMTP, with credentials managed
securely through a `.env` file.

```bash
cd task3-email-notifier
pip install -r requirements.txt
cp .env.example .env   # then fill in your Gmail address + App Password
python3 email_notifier.py customers.csv --dry-run
```

---

## Repository Structure
```
.
├── task1-web-scraper/
│   ├── property_scraper.py
│   ├── mock_site/
│   ├── property_listings.csv
│   └── README.md
├── task2-log-parser/
│   ├── log_parser.py
│   ├── sample_enquiries.txt
│   ├── generate_sample.py
│   └── README.md
├── task3-email-notifier/
│   ├── email_notifier.py
│   ├── customers.csv
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   └── README.md
└── README.md   (this file)
```

Each project folder has its own README with full setup instructions,
usage examples, and design notes specific to that task.

## Getting Started
Clone the repo and set up a virtual environment:
```bash
git clone <your-repo-url>
cd <repo-name>
python3 -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
```
Then follow the individual setup steps for whichever project you want to
run, listed above.

## Notes
- Task 1's scraper targets a bundled mock listings page by default (real
  estate sites like Zillow/99acres block simple scrapers) — see that
  project's README for how to point it at a real, permitted site.
- Task 3 requires a Gmail **App Password**, not your regular Gmail
  password — see that project's README for setup steps. Never commit a
  real `.env` file; only `.env.example` should be tracked in git.

## License
This project was built for educational/internship purposes.
