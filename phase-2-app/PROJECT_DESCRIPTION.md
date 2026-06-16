# HealthVerify India - Project Description

## Inspiration
When patients seek medical care, they often must trust hospitals and facilities at face value-especially during emergencies when time is critical. There's rarely an opportunity to verify whether advertised capabilities and specialties are accurate. This blind trust can lead to delays in proper treatment or mismatched care. We were inspired to build a solution that empowers patients with verified information, helping them find the right care when they need it most.

## What it does
HealthVerify India uses AI to cut through the noise and verify hospital claims against real data. The platform helps patients find facilities that truly match their medical needs by:
* Validating hospital certifications, specialties, and equipment against official records
* Providing symptom-based recommendations for appropriate care facilities
* Surfacing quality indicators and verified capabilities to support informed decisions
* Removing the burden of manual verification during critical moments

## How we built it
We leveraged the Databricks native stack for end-to-end development:
* **Lakebase** for synchronized, low-latency data access
* **Lakeflow Declarative Pipelines** for data ingestion and transformation
* **Unity Catalog** for governance and data organization
* **Model Serving** for AI-powered classification and recommendations
* **Databricks Apps** for deployment
* **Genie Code** for assisted development

The frontend is built with **Streamlit** for an intuitive user experience, and we used **Codex** for local deployment workflows.

## Challenges we ran into
The biggest technical hurdle was deploying the Databricks App from the workspace into the Apps environment-we had to pivot to using Codex locally to complete the deployment. Additionally, cleaning and validating healthcare facility data across multiple sources required careful pipeline design to handle inconsistencies and missing values.

## Accomplishments that we're proud of
Our exploratory data analysis uncovered meaningful signals in the facility data that we hadn't anticipated. We're particularly proud that we resisted the urge to jump straight into AI development, instead letting the data tell its story first. This data-driven approach shaped the features that actually matter to patients.

## What we learned
**Know your data first.** Spending time understanding data quality, patterns, and limitations upfront paid dividends throughout the project. The AI models are only as good as the foundation they're built on. We also learned the importance of user-centric design in healthcare-verification tools must be fast and accessible when every minute counts.

## What's next for HealthVerify India
* **Expand coverage**: Integrate additional data sources including patient reviews, accreditation databases, and real-time bed availability
* **Multilingual support**: Add regional language interfaces to serve diverse populations across India
* **Emergency routing**: Build real-time routing recommendations based on current facility capacity and patient condition
* **Provider dashboard**: Create a portal for hospitals to update their verified capabilities and respond to data discrepancies
* **Predictive insights**: Develop models to forecast facility capacity and suggest optimal timing for non-emergency procedures
* **Mobile app**: Launch a native mobile experience for faster access during emergencies
