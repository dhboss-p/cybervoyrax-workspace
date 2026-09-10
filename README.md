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

## Requirements

Before installation, make sure you have:

- Linux
- Git
- Docker
- Docker Compose v2 (`docker compose`)

## Installation

Clone the repository:

```bash
git clone https://github.com/dhboss-p/cybervoyrax-workspace.git
cd cybervoyrax-workspace
```

Create your local environment file:

```bash
cp .env.example .env
```

Before running the application, edit `.env` and replace the placeholder secrets and database passwords with local values.

Build and start the application:

```bash
docker compose up -d --build
```

Confirm that the containers are running:

```bash
docker compose ps
```

Provision the dedicated assessment account:

```bash
bash scripts/provision_lab_accounts.sh
```

The script generates the assessment password locally and stores it in the Git-ignored `.lab-credentials` file.

View your credentials:

```bash
cat .lab-credentials
```

They will look like:

```text
ASSESSMENT_EMAIL=assessor@cybervoyrax.test
ASSESSMENT_PASSWORD=<locally-generated-password>
```

Open the application in your browser:

```text
http://localhost:5000
```

If you changed `APP_PORT` in `.env`, use that port instead.

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

Start the workspace:

```bash
docker compose up -d
```

Stop the workspace:

```bash
docker compose down
```

Rebuild after local changes:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f web
```

Run the current structural verification:

```bash
docker compose exec web python scripts/verify_phase63.py
```

Run the account-baseline verification:

```bash
docker compose exec web python scripts/verify_account_baseline.py
```

## Data and uploads

Uploaded lab files persist under:

```text
./instance/uploads/
```

Use only fictional or disposable lab data. Do not upload real confidential or sensitive information to an intentionally vulnerable application.

## Resetting the lab

To stop the application without deleting the database volume:

```bash
docker compose down
```

To perform a full local reset, including the Docker database volume:

```bash
docker compose down -v
rm -f .lab-credentials
docker compose up -d --build
bash scripts/provision_lab_accounts.sh
```

**Warning:** `docker compose down -v` deletes the local database volume and therefore removes your current lab database state.

## Updating CYBERVOYRAX

CYBERVOYRAX is designed to support incremental releases. When an upgrade package is provided, follow the instructions included with that release.

Upgrade releases may create a backup, apply changed files, rebuild/restart the containers, and run release-specific verification. Release notes will state when a database migration or reset is required.

Do not assume every future release can be applied with the same commands; read the release notes first.

## Current release

**CYBERVOYRAX Workspace — Phase 6.3**

Phase 6.3 is the current baseline of the vulnerable Workspace environment. The exact vulnerability inventory is intentionally omitted to preserve the black-box assessment experience.

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
