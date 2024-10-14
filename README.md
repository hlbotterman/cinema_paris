# Cinema Paris Web Application

## Overview
This project is a web application that lists independent cinemas in Paris (referenced [here](https://www.cinemasindependantsparisiens.fr/les-cinemas/)), displays their schedules, and shows the locations on an interactive map. Built with Python and FastAPI, it provides users with an intuitive interface to explore movie schedules and cinema information.

The project is motivated by the fact that there is currently no single page where people can easily consult the screenings at independent cinemas in Paris. Instead, they have to visit each cinema's site individually, which makes difficult to get a complete overview of what's on offer.

## Features
- **Interactive Map**: Displays cinemas using Leaflet and OpenStreetMap.
- **Dynamic Scheduling**: View cinema schedules for the current and upcoming days.
- **Backend with FastAPI**: Efficient API built with FastAPI for fetching and rendering data.
- **Responsive Design**: Adapted for both desktop and mobile views.

## Installation

### Prerequisites
- Python 3.11 or higher
- Poetry (for managing dependencies)
- Git (to clone the repository)

### Setup Instructions
1. Clone the repository
   ```bash
   git clone https://github.com/your-username/cinema-paris.git
   cd cinema-paris

2. Install dependencies using Poetry
   ```bash
   poetry install
   poetry shell


3. Start the application
    ```bash
    uvicorn main:app --reload

4. Open your browser and navigate to http://localhost:8000 to access the application.
