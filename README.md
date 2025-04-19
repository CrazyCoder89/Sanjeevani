# Sanjeevani
# Hospital Management System (HMS)

## Overview

The Hospital Management System (HMS) is a comprehensive web application developed using Streamlit and MySQL. It integrates various healthcare functionalities, including patient management, doctor scheduling, risk analysis, length of stay predictions, and billing automation. This system is designed to improve hospital efficiency and patient care through AI-powered predictions and database-driven workflows.

## Features

- **Patient Management:** Track patient details, medical history, and ongoing treatments.
- **Doctor Dashboard:** Personalized view with survival analysis, LOS prediction, risk analysis, and past medical records.
- **Scheduling System:** Doctors can set availability, and staff can book patient appointments.
- **AI-Powered Predictions:** Models for cardiovascular risk, survival analysis, ICU/ward length of stay prediction, and air pollution disease prediction.
- **Billing System:** Automated billing for medicines, injections, and hospital services.
- **Telemedicine Integration:** Remote consultations for improved accessibility.
- **Bed & Surgery Scheduling:** Allocate beds and track scheduled surgeries.
- **Automated Reminders:** Email/SMS notifications for appointments and follow-ups.

## Technologies Used

- **Frontend:** Streamlit (Python)
- **Backend:** MySQL
- **Machine Learning Models:** Random Forest, XGBoost, ClinicalBERT
- **Database Management:** MySQL Workbench

## Installation

### Prerequisites

- Python 3.x
- MySQL Server & MySQL Workbench
- Streamlit and required Python libraries

### Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/your-repo/hms.git
   cd hms
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Configure the MySQL database:

   - Create a database in MySQL.
   - Run the schema SQL script to set up tables.
   - Update `config.py` with database credentials.

4. Run the application:

   ```sh
   streamlit run app.py
   ```

## Usage

- **Admin & Staff:** Manage hospital operations, schedule appointments, and track patients.
- **Doctors:** Access dashboards for predictive analysis, scheduling, and telemedicine.
- **Patients:** Book appointments and view medical records.

## Future Enhancements

- **EHR Integration:** Connect with external electronic health records.
- **Mobile App:** Develop a mobile-friendly interface.
- **Advanced AI Models:** Improve predictions with deep learning models.

## Contributing

Feel free to contribute by submitting issues or pull requests. Follow the contribution guidelines in `CONTRIBUTING.md`.

## License

This project is licensed under the MIT License.

## Contact

## Contact

For queries, contact: [shahkrish501@gmail.com](mailto:shahkrish501@gmail.com)


