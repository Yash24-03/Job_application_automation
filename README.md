
# Job Application Automation

## Overview

This project automates the process of fetching job application emails, extracting relevant information such as the company name and job title, and updating a Notion database with this information. The script uses IMAP to access the email server, and the Notion API to update the database.

## Features

- Authenticate to an email server using IMAP.
- Fetch job application emails.
- Extract company name and job title from emails.
- Update a Notion database with extracted information.
- Handle errors during the process.

## Prerequisites

- Python 3.x
- A Gmail account with IMAP enabled.
- Notion API token and database ID.
- `.env` file with the following environment variables:
  - `EMAIL_USERNAME`: Your email address.
  - `EMAIL_PASSWORD`: Your email password.
  - `NOTION_TOKEN`: Your Notion integration token.
  - `NOTION_DATABASE_ID`: The ID of the Notion database to update.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/job-application-automation.git
   cd job-application-automation
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory of the project with your credentials:
   ```plaintext
   EMAIL_USERNAME=your_email@example.com
   EMAIL_PASSWORD=your_password
   NOTION_TOKEN=your_notion_token
   NOTION_DATABASE_ID=your_database_id
   ```

## Usage

1. Run the script:
   ```bash
   python job_application_automation.py
   ```

2. The script will authenticate to your email server, fetch job application emails, extract the company name and job title, and update the specified Notion database.

## Script Structure

- `authenticate_email(username, password, imap_url)`: Authenticates to the email server.
- `fetch_job_application_emails(mail)`: Fetches job application emails.
- `extract_company_name_and_position(msg)`: Extracts the company name and job title from the email.
- `update_notion_database(company_name, position, email_date)`: Updates the Notion database with the extracted information.
- `main()`: Main function to run the script.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [IMAPLIB](https://docs.python.org/3/library/imaplib.html) for email fetching.
- [Notion API](https://developers.notion.com/) for database updates.
- [dotenv](https://pypi.org/project/python-dotenv/) for managing environment variables.
