# CV Building Assistant

This project is a CV building assistant that helps users create comprehensive CVs through a conversational interface. It utilizes the OpenAI API to generate responses and extract relevant information from user inputs.

## Project Structure

```
cv-building-assistant
├── src
│   ├── main.py                  # Entry point of the application
│   ├── agents                   # Contains agent classes for CV building
│   │   ├── cv_agent.py          # Manages the CV building process
│   │   └── conversation_manager.py # Manages conversation history
│   ├── models                   # Contains data models
│   │   ├── cv_data.py           # Represents CV data structure
│   │   └── conversation.py       # Represents a conversation instance
│   ├── services                 # Contains service classes
│   │   ├── openai_service.py     # Handles OpenAI API calls
│   │   └── data_extraction.py    # Functions for extracting CV data
│   ├── utils                    # Contains utility functions
│   │   ├── validators.py         # Validates user input
│   │   └── formatters.py         # Formats CV data and responses
│   └── ui                       # Contains UI components
│       ├── streamlit_app.py      # Streamlit application code
│       └── components            # UI components
│           ├── chat_interface.py  # Manages chat interface
│           └── progress_tracker.py # Tracks user progress
├── tests                        # Contains unit tests
│   ├── test_cv_agent.py          # Tests for CvAgent class
│   ├── test_conversation_manager.py # Tests for ConversationManager class
│   └── test_data_extraction.py    # Tests for data extraction functions
├── config                       # Configuration settings
│   ├── settings.py               # Application configuration
├── requirements.txt             # Project dependencies
├── .env.example                 # Example environment variables
├── .gitignore                   # Files to ignore by Git
└── README.md                    # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd cv-building-assistant
   ```

2. **Create a virtual environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Copy `.env.example` to `.env` and fill in the required values.

5. **Run the application**:
   ```
   python src/main.py
   ```
6. **Run the following to test the aapplication**:
   ```
   python -m unittest tests/test_conversation_manager.p
   ```

## Usage

- Open the application in your web browser.
- Follow the prompts to provide information for your CV.
- The assistant will guide you through the process and help you complete your CV.

## Contribution Guidelines

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and create a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.