# CYBERVOYRAX Workspace

**A deliberately vulnerable, realistic SaaS workspace for hands-on black-box web application penetration testing and security training.**

CYBERVOYRAX Workspace is a self-hosted training application designed to feel like a normal internal business platform rather than a collection of labelled security challenges.

The goal is simple: approach the application as you would an authorized real-world web application assessment. Explore it, map its functionality, form hypotheses, test security boundaries, validate findings, demonstrate impact, and write a professional report.

The project intentionally does **not** reveal vulnerable endpoints, parameters, payloads, object IDs, vulnerability counts, or solution paths in this README.

## What the application simulates

CYBERVOYRAX Workspace represents a fictional company collaboration environment with realistic application functionality, including:

- user accounts and authentication
- profiles and account management
- projects and workspace resources
- documents and file handling
- notifications
- administrative functionality
- server-side application features

Some functionality is intentionally vulnerable and some is intentionally secure. A strange request or unusual behavior is not automatically a vulnerability; testers are expected to validate security impact.

Additional business functionality will be introduced as the project grows.

## Who this is for

CYBERVOYRAX Workspace is intended for cybersecurity students and practitioners who want practical experience with:

- web application penetration testing
- ethical hacking
- attack-surface mapping
- manual vulnerability discovery
- Burp Suite and HTTP analysis
- authentication and authorization testing
- server-side and application-logic testing
- vulnerability validation
- penetration-test reporting

A basic understanding of HTTP requests and responses, cookies, sessions, authentication, and common web concepts is recommended.

## Black-box testing experience

For the intended experience, **do not inspect the source code before testing**.

You are not given a vulnerability checklist, challenge selector, flag list, payload guide, or solution walkthrough. Instead, treat the application as if a client handed you a web application and said:

> **Assess this application and tell us what you can find.**

You may use the same methodology and tools you would use during an authorized web application penetration test.

## Prerequisites

CYBERVOYRAX runs inside Docker. You do not need to manually install Python, Flask, Gunicorn, MySQL, or the application's Python dependencies on your host system.

Before installation, make sure you have:

- Linux
- Git
- Docker
- Docker Compose v2 (`docker compose`)
- a running Docker daemon

After cloning the repository, you can check your environment with:

```bash
bash scripts/check_requirements.sh
```

If a required component is missing, the check will stop and tell you what needs to be installed or fixed.

## Quick start

Clone the repository:

```bash
git clone https://github.com/dhboss-p/cybervoyrax-workspace.git
cd cybervoyrax-workspace
```

Create your local environment file:

```bash
cp .env.example .env
```

Review `.env` and replace the placeholder secrets and database passwords with local values.

Then run:

```bash
bash scripts/setup.sh
```

The setup script will check the environment, build the application, start the database, initialize the workspace, provision the assessment account, and verify the installation.

When setup completes, open:

```text
http://127.0.0.1:5000
```

If you changed `APP_PORT` in `.env`, use that port instead.

## Creating an account

CYBERVOYRAX supports local user registration. Open the application and select **Create Account** from the sign-in page.

New users choose their own password and department during registration. Accounts created through the registration page are standard workspace users.

Users in the same CYBERVOYRAX installation share the same fictional company workspace. Projects can be shared through project membership, while company-wide resources such as the **Internal Knowledge Base** are available across the workspace.

Each cloned installation uses its own local database. Accounts and workspace data are not shared between separate CYBERVOYRAX installations.

## Assessment credentials

Your locally generated assessment credentials are stored in:

```text
.lab-credentials
```

View them with:

```bash
cat .lab-credentials
```

They will look like:

```text
ASSESSMENT_EMAIL=assessor@cybervoyrax.test
ASSESSMENT_PASSWORD=<locally-generated-password>
```

Never commit `.lab-credentials` or `.env`.

## Assessment account

The dedicated assessment account is a normal low-privilege starting account for authorized black-box testing.

Other fictional users and privileged accounts exist inside the workspace as realistic background users and resource owners. Their credentials are intentionally not published.

The supplied assessment credential is **not itself a vulnerability**. It provides legitimate authenticated access from which you can assess the application's security boundaries.

Never commit `.lab-credentials` or `.env`. Both are intended to remain local.

## Recommended testing approach

There is deliberately no required solution order. A reasonable assessment workflow is:

**Reconnaissance → application mapping → authentication testing → session analysis → access-control testing → input testing → file/functionality testing → server-side testing → business-logic testing → exploitation → reporting**

Browser developer tools, Burp Suite, curl, and other standard web-testing utilities can be used. Automated tools may assist your assessment, but the platform is designed to reward understanding application behavior rather than simply running scanners.

## Reporting findings

Treat the exercise like a real penetration-test engagement. For each confirmed finding, consider documenting:

- title
- severity
- affected functionality
- description
- steps to reproduce
- supporting HTTP requests/responses or screenshots
- security impact
- remediation

Severity should be based on the actual exploitability and impact you demonstrate, not only the vulnerability class name.

## Useful commands

Start an existing workspace:

```bash
docker compose up -d
```

Stop the workspace without deleting its database:

```bash
docker compose down
```

Check container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f web
```

Rebuild the application while preserving the database:

```bash
docker compose up -d --build
```

Check the local environment:

```bash
bash scripts/check_requirements.sh
```

Run the account-baseline verification:

```bash
docker compose exec web python scripts/verify_account_baseline.py
```

## Password recovery

Users can select **Forgot password?** on the sign-in page to start the local password-recovery flow.

The assessment credentials in `.lab-credentials` are generated when the assessment account is first provisioned. Normal restarts, rebuilds, setup runs, and updates do not rotate the password.

If assessment access is lost, explicitly generate a new password with:

```bash
bash scripts/reset_assessment_password.sh
```

The reset workflow updates the assessment account and refreshes `.lab-credentials`. Existing user passwords are not changed.

## Data and persistence

CYBERVOYRAX separates application source code from runtime lab data.

Persistent application data includes user accounts, projects, comments, document metadata, activity records, and other workspace state stored in the MySQL Docker volume.

Uploaded files persist under:

```text
./instance/uploads/
```

Assessment credentials are stored locally in:

```text
.lab-credentials
```

Local configuration is stored in:

```text
.env
```

Normal container restarts, rebuilds, and CYBERVOYRAX updates are designed to preserve this data.

Use only fictional or disposable lab data. Do not upload real confidential or sensitive information to an intentionally vulnerable application.

## Updating CYBERVOYRAX

For a normal Git-based installation, update CYBERVOYRAX with:

```bash
bash scripts/update.sh
```

Before applying an update, the updater creates a local backup and checks that it can safely update the installation. Required workspace migrations are applied without resetting the existing database.

Normal updates are designed to preserve:

- user accounts and passwords
- assessment credentials
- projects and comments
- document metadata and uploaded files
- workspace database state
- local `.env` configuration

Upgrade backups are stored under:

```text
.upgrade-backups/
```

The updater will not overwrite tracked source files containing uncommitted modifications. If this happens, review them with:

```bash
git status
git diff
```

The assessment account is not reprovisioned during a normal update, so the existing assessment credentials remain valid.

Release-specific instructions should still be reviewed when a release contains unusual or breaking changes.

## Resetting the lab

To stop CYBERVOYRAX without deleting the database:

```bash
docker compose down
```

This is safe for normal use.

### Full destructive reset

To completely remove the local database and return to a fresh lab state:

```bash
docker compose down -v
rm -f .lab-credentials
docker compose up -d --build
bash scripts/provision_lab_accounts.sh
```

**Warning:** `docker compose down -v` deletes the CYBERVOYRAX MySQL Docker volume. This permanently removes the current database state, including accounts, projects, comments, document metadata, and other database-backed lab activity.

A normal CYBERVOYRAX update does **not** require `docker compose down -v`.

## Troubleshooting

Check whether the required environment is available:

```bash
bash scripts/check_requirements.sh
```

Check the containers:

```bash
docker compose ps
```

View recent application logs:

```bash
docker compose logs --tail=100 web
```

View recent database logs:

```bash
docker compose logs --tail=100 db
```

If Docker cannot connect to the Docker daemon, make sure Docker is running and that your user has permission to access it.

If port `5000` is already in use, change `APP_PORT` in `.env` and start the workspace again.

Avoid deleting Docker volumes as a general troubleshooting step because doing so destroys the local database.

## Current release

**CYBERVOYRAX Workspace — Phase 6.4**

Phase 6.4 is the current baseline of the vulnerable Workspace environment. The exact vulnerability inventory is intentionally omitted to preserve the black-box assessment experience.

## Safety

CYBERVOYRAX Workspace is **intentionally vulnerable**.

Run it only in an environment you control, such as your own computer, an isolated virtual machine, or a private lab network. **Do not expose it directly to the public internet.**

Only use the techniques practiced with CYBERVOYRAX against systems you own or have explicit authorization to test.

## Project philosophy

CYBERVOYRAX is not designed around:

> Click a challenge → get told the vulnerability → paste a payload → capture a flag.

The intended experience is closer to:

> **Here is an application. You have authorization to test it. Figure out what is wrong.**

The objective is not simply to collect vulnerability names. The objective is to practice conducting a web application penetration test: discovering functionality, understanding trust boundaries, validating vulnerabilities, demonstrating impact, and communicating findings clearly.

## Roadmap

CYBERVOYRAX Workspace will continue to grow with additional realistic business functionality and progressively deeper assessment scenarios. New functionality is intended to expand the attack surface without turning the interface into a visible challenge board.

## Contributing

Contributions, fixes, and improvements are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting changes.

Because the application is intentionally vulnerable, please avoid publicly disclosing planted vulnerability locations or solution paths in general-purpose issues or pull-request descriptions unless the discussion specifically requires them.

For security information, see [`SECURITY.md`](SECURITY.md).

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See [`LICENSE`](LICENSE) for the complete license text.

## Author & maintainer

**Praise Testimony — CYBERVOYRAX**

- GitHub: [@dhboss-p](https://github.com/dhboss-p)
- LinkedIn: [Praise Testimony — CYBERVOYRAX](https://linkedin.com/in/praise-testimony-cybervoyrax)

---

**CYBERVOYRAX Workspace is provided for education, authorized security testing, and cybersecurity training.**
