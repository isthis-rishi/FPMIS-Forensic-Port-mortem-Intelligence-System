# FPMIS --- Forensic Post-Mortem Intelligence System

> **Transforming forensic investigations with digital intelligence.**

FPMIS is a digital platform concept and web application for organizing
forensic post-mortem case information in one place. Developed by
**Digital Care Crew**, it brings case management, autopsy documentation,
time-of-death (TOD) estimation, decomposition tracking, evidence
records, missing-person matching, pattern alerts, and cross-case search
into a unified workflow.

**Live project:** <https://fpmis.gurindersingh.dev>

> **Important:** FPMIS is an investigation-support tool. Any estimates,
> matches, or alerts must be reviewed by qualified forensic and
> investigative professionals. They are not definitive findings and must
> not replace expert examination, validated procedures, or applicable
> legal requirements.

------------------------------------------------------------------------

## Contents

-   [Overview](#overview)
-   [Problem and Goals](#problem-and-goals)
-   [Key Features](#key-features)
-   [How the Workflow Fits Together](#how-the-workflow-fits-together)
-   [Technical Architecture](#technical-architecture)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Local Installation](#local-installation)
-   [Configuration Notes](#configuration-notes)
-   [Running the Application](#running-the-application)
-   [Core Logic](#core-logic)
-   [Security and Data Handling](#security-and-data-handling)
-   [Testing and Verification](#testing-and-verification)
-   [Troubleshooting](#troubleshooting)
-   [Roadmap](#roadmap)
-   [Team](#team)
-   [Limitations and Disclaimer](#limitations-and-disclaimer)
-   [License](#license)

------------------------------------------------------------------------

## Overview

Forensic case information can be spread across paper records, separate
departments, and disconnected workflows. This can make it harder to
maintain consistent records, trace evidence, compare unidentified bodies
with missing-person reports, and notice similarities between cases.

FPMIS proposes a centralized digital workflow to help authorized users
organize case data and review relevant information across cases. The
platform is organized around eight modules that cover the core
activities described in the project presentation.

### Project goals

-   Centralize forensic case information in a structured digital system.
-   Support consistent case status tracking and documentation.
-   Record autopsy findings and injury information digitally.
-   Provide a multi-parameter tool for estimating a possible
    time-of-death range.
-   Track decomposition observations and relevant environmental factors.
-   Maintain evidence handling and transfer records.
-   Help investigators review possible missing-person matches.
-   Surface potentially relevant similarities between cases.

## Problem and Goals

The project presentation identifies four challenges the system is
intended to address:

1.  **Paper-based records:** Manual documentation can lead to errors,
    delays, or missing information.
2.  **Fragmented records:** Case information may be spread across
    departments without a unified view.
3.  **Delayed identification:** Comparing unidentified bodies with
    missing-person reports can be time-consuming.
4.  **Limited cross-case analysis:** Similarities between cases may be
    difficult to recognize without structured searching and comparison.

FPMIS addresses these challenges through digital case records, matching
support, evidence tracking, and cross-case analysis. The impact figures
shown in the project documentation are project targets/expected impact, not
independently verified production results.

## Key Features

FPMIS is presented as eight connected modules.

### 1. Case Management

Provides a central place to create and track forensic cases.

-   Unique case-number format shown in the project documentation:
    `FPMIS/YYYY/XXXXX`
-   Support for multiple case types
-   High, medium, and low priority levels
-   Police-station and FIR linking
-   Case status tracking
-   Audit-trail support
-   Multi-institution workflow as a stated design capability

### 2. Autopsy Reports

Supports structured digital documentation of post-mortem examinations.

-   Deceased-person information
-   External examination notes
-   Internal examination findings
-   Cause-of-death documentation
-   Manner-of-death classification
-   Injury logging and body mapping
-   Digital-signature support as a stated capability

### 3. Time of Death (TOD) Calculator

The TOD calculator is designed to estimate a possible time-since-death
range using multiple inputs. The presentation identifies these
parameters:

-   Body temperature
-   Ambient temperature
-   Body weight
-   Rigor mortis observations, using a four-region scale
-   Livor mortis fixation
-   Corneal opacity
-   Potassium levels

The intended output includes an estimated TOD range, a confidence level,
contributing factors, reasoning, and an analysis of individual
parameters. The presentation describes the approach as based on the
**Henssge nomogram and multi-factor analysis**. Actual reliability
depends on the implementation, data quality, environmental context, and
professional interpretation.

### 4. Decomposition Tracking

Records decomposition observations across seven stages:

1.  Fresh
2.  Early decomposition
3.  Bloat
4.  Active decay
5.  Advanced decay
6.  Dry remains
7.  Skeletonization

Contextual observations include
temperature, humidity, weather, indoor/outdoor location, sun exposure,
insect activity, maggot stage, bloating level, and other body changes.
Stage durations shown in the project documentation are indicative ranges, not
universal rules.

### 5. Evidence Management and Chain of Custody

Organizes evidence records and supports tracking of evidence handling
through the investigation.

Example evidence categories listed in the project documentation include:

-   Biological samples and DNA samples
-   Clothing and personal belongings
-   Weapons
-   Documents
-   Electronic devices
-   Toxicology samples

The intended chain-of-custody record includes transfer history,
timestamps, handler identification, location, condition notes,
digital-signature support, and report preparation. A digital record
alone does not guarantee legal admissibility; actual procedures and
system controls must meet applicable requirements.

### 6. Missing-Person Matching

Supports comparison between unidentified-body records and missing-person
reports using a weighted score.

The matching criteria and weights are:

  Matching criterion               Weight
  ---------------------- ----------------
  Gender match                  20 points
  Age range (±5 years)          15 points
  Height (±5 cm)                15 points
  Build type                    10 points
  Hair color                    10 points
  Identification marks          20 points
  Other features                10 points
  **Total**                **100 points**

The score bands are:

  Score band   Label in presentation
  ------------ -----------------------
  80--100%     High
  60--79%      Medium
  30--59%      Low

These are candidate-ranking indicators, not identity confirmation. A low
score is not proof that two records are unrelated, and a high score must
be checked against appropriate evidence and professional procedures. The
presentation does not specify the handling of scores below 30%.

### 7. Pattern Detection and Alerts

Helps surface potentially suspicious similarities across cases. The
presentation identifies four pattern categories:

-   **Geographic:** multiple cases in the same area within a short
    period.
-   **Cause of death:** repeated or similar causes of death.
-   **Demographic:** similarities in age, gender, or other victim
    characteristics.
-   **Temporal:** cases occurring at similar times or intervals.

Alerts should be treated as leads for review, not as proof of a
connection or criminal activity.

### 8. Smart Search

Supports cross-case queries so users can find and compare relevant
records more efficiently. The precise search fields, query syntax, and
indexing implementation are not specified in the supplied project
materials.

## How the Workflow Fits Together

A typical workflow is:

1.  Create a new forensic case.
2.  Add the autopsy report and injury information.
3.  Calculate a possible time-of-death range.
4.  Log evidence and its chain-of-custody details.
5.  Run missing-person matching.
6.  Review pattern alerts and related cases.

The modules are intended to work together so that case details,
examination notes, evidence records, matching results, and cross-case
observations can support a more organized investigation workflow.

## Technical Architecture

FPMIS follows a layered architecture:

``` text
┌────────────────────────────────────────────┐
│ Client Layer                               │
│ Next.js 14 · React 18 · TypeScript         │
└──────────────────────┬─────────────────────┘
                       │ HTTP/API requests
┌──────────────────────▼─────────────────────┐
│ API Layer                                  │
│ FastAPI · JWT Authentication               │
└──────────────────────┬─────────────────────┘
                       │
┌──────────────────────▼─────────────────────┐
│ Business Logic                             │
│ SQLAlchemy ORM · Matching Algorithms       │
└──────────────────────┬─────────────────────┘
                       │
┌──────────────────────▼─────────────────────┐
│ Data Layer                                 │
│ PostgreSQL 16 · UUID · JSONB               │
└────────────────────────────────────────────┘
```

### Architecture responsibilities

-   **Client layer:** Presents pages and interactive workflows to users.
-   **API layer:** Exposes backend operations through FastAPI and uses
    JWT-based authentication according to the project design.
-   **Business-logic layer:** Applies application rules and matching
    logic, with SQLAlchemy used to work with database records.
-   **Data layer:** PostgreSQL stores structured relational records; the
    presentation identifies UUID primary keys and JSONB support.

The diagram represents the architecture described in the supplied
presentation. Exact API routes, database migrations, authentication
flows, and deployment configuration should be confirmed against the
source code.

## Technology Stack

  -----------------------------------------------------------------------
  Layer                               Technologies
  ----------------------------------- -----------------------------------
  Frontend                            Next.js 14, React 18, TypeScript,
                                      Tailwind CSS, Axios

  Backend                             Python 3.11+, FastAPI, SQLAlchemy
                                      ORM, Pydantic, JWT authentication

  Database                            PostgreSQL 16, relational schema,
                                      UUID primary keys, JSONB support

  Data and auditing                   Structured records and audit-log
                                      capability described in the
                                      presentation
  -----------------------------------------------------------------------

## Project Structure

The repository is organized as follows:

``` text
FPMIS/
├── backend/
│   ├── app/
│   │   ├── models/       # Database models
│   │   ├── routers/      # API endpoints
│   │   └── schemas/      # Pydantic schemas
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js pages and routes
│   ├── components/       # Reusable React components
│   └── lib/              # Frontend utilities
└── database/
    └── schema.sql        # Database schema
```

This is the structure documented in the supplied README. If your current
repository differs, update this tree to match the actual files before
publishing.

## Local Installation

These instructions follow the supplied README and project stack. They
assume the repository contains the documented `backend/` and `frontend/`
directories.

### Prerequisites

Install the following software:

-   **Git** --- to clone the repository.
-   **Node.js 18 or later** and npm --- for the Next.js frontend.
-   **Python 3.11 or later** --- for the FastAPI backend.
-   **PostgreSQL 16** --- for the application database.

Verify your installations:

``` bash
git --version
node --version
npm --version
python --version
psql --version
```

On some systems, use `python3` instead of `python`.

### 1. Clone the repository

Replace `<repository-url>` with the clone URL shown on your GitHub
repository page.

``` bash
git clone <repository-url>
cd FPMIS
```

If your local folder has a different name, change into that folder
instead.

### 2. Create the PostgreSQL database

Start PostgreSQL and open `psql` as a database administrator. Create a
database and a dedicated application user:

``` sql
CREATE DATABASE fpmis;
CREATE USER fpmis_user WITH PASSWORD 'replace-with-a-strong-password';
GRANT ALL PRIVILEGES ON DATABASE fpmis TO fpmis_user;
```

The SQL above follows the database-creation approach in the supplied
README, but uses a placeholder password instead of a reusable example
credential.

**Important:** Database permissions and schema privileges can vary by
PostgreSQL version and setup. If the application cannot create or access
tables, check the database owner's permissions and the project's schema
or migration instructions.

If the repository contains `database/schema.sql`, inspect it and apply
it if it is the intended initialization script. For example, from a
terminal where `psql` is configured:

``` bash
psql -U fpmis_user -d fpmis -f database/schema.sql
```

If the project uses migrations or initializes tables from application
code, follow that implementation instead. The supplied materials do not
specify a migration command.

### 3. Set up the backend

Open a terminal at the repository root.

#### Windows --- PowerShell

``` powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, use a permitted
activation method for your system or run the equivalent commands in
Command Prompt:

``` bat
venv\Scripts\activate.bat
```

#### macOS / Linux

``` bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the API using the command documented in the supplied README:

``` bash
python -m uvicorn app.main:app --reload --port 8000
```

This expects `backend/app/main.py` to expose the FastAPI application as
`app`. If that import path differs in your checked-out source, use the
entry point defined by your implementation.

### 4. Configure backend database access

The backend needs to connect to the PostgreSQL database created above.
The supplied files do not specify the exact environment-variable names
or configuration-loading mechanism.

1.  Inspect the backend configuration and database connection code.
2.  Identify how the application reads its database URL, JWT secret, and
    other settings.
3.  Configure those values using the mechanism the code expects.
4.  Use a strong, private database password and JWT secret.
5.  Keep local secrets out of Git; add local environment files to
    `.gitignore`.

A database URL often follows this general pattern, but the exact
variable name must come from your code:

``` text
postgresql://fpmis_user:<your-password>@localhost:5432/fpmis
```

Do not commit real passwords, signing secrets, tokens, or sensitive
forensic records.

### 5. Set up the frontend

Open a **second terminal** at the repository root:

``` bash
cd frontend
npm install
npm run dev
```

Use `npm run dev` for local development, provided the frontend's `package.json` contains that script. The
frontend's `package.json` must contain that script. If it does not,
inspect the scripts available in that file rather than assuming a
different command.

If the frontend requires an API base URL, inspect its Axios
configuration and configure the expected value for your local backend.
The exact variable name is not documented in the supplied materials, so
do not assume one.

### 6. Open the application

With the backend and frontend running, open the local address printed by
the Next.js development server in your terminal. The standard Next.js
development port is commonly `3000`, but use the address actually
printed by your setup.

The backend command above listens on port `8000`. If the frontend cannot
reach it, verify the API base URL, CORS configuration, and that both
processes are running.

## Configuration Notes

The supplied files document the stack and basic startup commands, but do
**not** provide a complete configuration reference. Before publishing or
deploying, confirm these items in the source code:

-   Database URL or individual PostgreSQL connection settings
-   JWT signing secret, token expiry, and authentication configuration
-   CORS allowed origins
-   Frontend API base URL
-   Required environment-variable names
-   Schema initialization or migration procedure
-   File or evidence attachment storage, if implemented
-   Production build and deployment commands

Do not add made-up `.env` keys to the README. Document the actual keys
after checking the code, and consider including a sanitized
`.env.example` with placeholder values.

## Core Logic

### Time-of-death estimation

The TOD module accepts multiple body and environmental observations and
is intended to return a range with explanatory factors. The presentation
references the Henssge nomogram and multi-factor analysis, but the
supplied README and presentation do not include the implementation
formula, calibration details, validation dataset, or scientific
performance results. These should be documented separately if they are
available in the code or project research.

### Missing-person matching

The presentation describes a weighted score out of 100 using seven
criteria. The resulting score is grouped into high, medium, and low
confidence bands. This supports prioritizing candidate records for
review; it does not establish identity.

### Pattern detection

The design looks for similarities across geographic, cause-of-death,
demographic, and temporal dimensions. The exact thresholds, clustering
method, and alert-generation rules are not specified in the supplied
materials and should be documented from the implementation if
applicable.

## Security and Data Handling

The presentation describes a security-first design with JWT
authentication, role-based access control, encrypted data, secure API
endpoints, and audit trails. Treat these as design goals unless each
control has been verified in the deployed application.

For a system that may handle sensitive forensic and personal
information:

-   Use authentication and least-privilege authorization for protected
    records.
-   Keep secrets in environment configuration or a secrets manager,
    never in source control.
-   Use HTTPS in deployed environments.
-   Validate and authorize requests on the server, not only in the
    frontend.
-   Restrict access to sensitive records and evidence attachments.
-   Avoid using real personal or forensic data in development and demo
    environments.
-   Protect logs from leaking tokens, credentials, or sensitive case
    details.
-   Back up the database securely and test restoration procedures.
-   Maintain and review audit records for important access and changes.
-   Follow applicable privacy, evidence-handling, retention, and legal
    requirements.

Security claims should be validated against the implementation and
deployment configuration before being presented as guarantees.

## Testing and Verification

The supplied project materials do not document a test suite or test
commands. For a local smoke test, verify the following manually or
through automated tests where available:

-   [ ] The frontend starts successfully.
-   [ ] The backend starts and can connect to PostgreSQL.
-   [ ] Database schema initialization completes without errors.
-   [ ] Case records can be created and retrieved, if the relevant
    workflow is implemented.
-   [ ] Autopsy and evidence forms validate input as expected.
-   [ ] TOD calculations show their inputs and outputs clearly.
-   [ ] Matching results display scores and confidence labels
    consistently.
-   [ ] Pattern alerts and cross-case search behave as intended.
-   [ ] Protected API operations enforce authentication and
    authorization.
-   [ ] Sensitive values are not exposed in frontend bundles or logs.

Do not use real case data for testing unless you have the necessary
authorization and safeguards.

## Troubleshooting

### `pip install -r requirements.txt` fails

-   Confirm that the virtual environment is active.
-   Check that the installed Python version meets the requirement
    (Python 3.11+).
-   Read the package error carefully; some dependencies may require
    platform-specific system libraries.

### `app.main` cannot be imported by Uvicorn

-   Confirm you are running the command from the `backend/` directory.
-   Verify that `backend/app/main.py` exists.
-   Check that it exposes a FastAPI instance named `app`.
-   If the project uses a different entry point, adjust the Uvicorn
    import path to match the source.

### PostgreSQL connection errors

-   Confirm the PostgreSQL service is running.
-   Check the database name, username, password, host, and port.
-   Confirm that the configured database URL matches the settings
    expected by the backend.
-   Check database and schema privileges and apply the project's schema
    or migrations if needed.

### Frontend cannot connect to the backend

-   Confirm the API is running on the expected port.
-   Inspect the frontend's Axios configuration and API base URL.
-   Check the backend's CORS settings for the local frontend origin.
-   Inspect the browser console and backend logs, taking care not to
    expose secrets.

### `npm run dev` is missing

-   Make sure you are in the `frontend/` directory.
-   Check `frontend/package.json` for a `dev` script.
-   Install dependencies with `npm install`.
-   Use only the development command defined by the project's package
    scripts.

## Roadmap

The presentation lists the following planned phases. These are roadmap
items, not a claim that every item is already implemented:

-   **Core release:** Eight core modules, web platform, PostgreSQL
    backend.
-   **Mobile and offline support:** Mobile app, offline mode, and
    biometric integration.
-   **Advanced intelligence:** AI-powered facial matching and advanced
    analytics.
-   **Broader integration:** National database integration and
    multilingual support.

The presentation associates these phases with 2026 quarters. Check the
current project status before describing any roadmap item as delivered.

## Team

| Name | Role |
|---|---|
| [Gurinder Singh](https://fpmis.gurindersingh.dev) | Team Lead |
| [Rishi Kumar](https://github.com/isthis-rishi) | Full Stack Developer |
| [Shantanu Pandit](https://github.com/ShantanuInnovates) | Backend Developer |
| [Jatin Guleria](https://github.com/JatinCodes020304) | Frontend Developer |
| [Vishal Mishra](https://fpmis.gurindersingh.dev) | UI/UX Designer |

## Limitations and Disclaimer

FPMIS is intended to organize information and support forensic
workflows. Its calculations, matching scores, and alerts should be
treated as decision-support outputs that require independent review.

-   A matching score is not proof of identity.
-   A pattern alert is not proof of a crime or connection between cases.
-   A TOD estimate is not a definitive determination of time of death.
-   Decomposition timelines vary with environmental and case-specific
    conditions.
-   Evidence records do not by themselves guarantee chain-of-custody
    compliance or legal admissibility.

Use the system only in accordance with applicable law, institutional
policy, and professional forensic standards. The project presentation's
impact figures are expected outcomes, not verified performance
benchmarks.

## License

The supplied README identifies the project as **Proprietary --- All
Rights Reserved**. No open-source license is specified. Do not assume
others may copy, modify, or redistribute the project unless the owners
provide permission or add an appropriate license.

------------------------------------------------------------------------

**Live project:**
[fpmis.gurindersingh.dev](https://fpmis.gurindersingh.dev)

*Built by Digital Care Crew --- Technology for Justice.*
