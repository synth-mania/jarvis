# Jarvis Personal Assistant

A command-line personal assistant that integrates with Google Calendar, Gmail, and Tasks to help manage your digital life.

## Features

- Compatible with any OpenAI-type LLM inference API endpoint. (Openrouter, OpenAI, LMStudio, llama.cpp, etc)
- Gmail integration (view unread emails)
- Google Calendar integration (check upcoming events) 
- Google Tasks tracking (view tasks)

## Prerequisites

- Python 3.12+
- Google account with API access enabled for:
  - Gmail API
  - Google Calendar API
  - Google Tasks API
- Google Cloud project credentials (`credentials.json`)
- An openrouter.ai API key

## Installation


1. Clone the repository
2. Place your `credentials.json` file in the `src/data_sources/` directory
3. Create a file named .env with environment variables in the root directory:


```bash
# For OpenRouter
LLM_API_TYPE=openrouter
OPENROUTER_API_KEY=your_key_here

USE_CALENDAR=enabled # enabled or disabled
USE_TASKS=enabled
USE_GMAIL=enabled

# For local API
#LLM_API_TYPE=local
#LOCAL_API_KEY=your_local_key_here
#LOCAL_API_URL=http://localhost:1234/v1/chat/completions
#LOCAL_MODEL_NAME=your-local-model-name
```

4. Run the setup/start script:
```bash
./start-jarvis.sh
```

Jarvis will start after creating a python venv and installing prerequisites. 

## Usage

Basic usage:

Navigate to the root directory of the repository, then execute the following bash command:
```bash
./start-jarvis.sh
```

## First Run Setup

On first run, you'll need to:

1. Authorize access to your Google account
    - by opening the link printed to the console
2. Grant permissions for Calendar, Gmail and Tasks access
    - When Jarvis first tries to access each of these APIs, an error message will be printed to console. Click the link in that message to be brough to a google page where you can activate that API. Your next message requesting info from that API should work, provided your credentials.json has been set up properly.
3. Token files will be created automatically for future use in /src/data_sources

## Commands

- Type 'quit' to exit
- Any message mentioning one or more of your tasks, email, or calendar, directly or indirectly, will cause the relevant API(s) to be polled for info which will be included as context for your prompt.
