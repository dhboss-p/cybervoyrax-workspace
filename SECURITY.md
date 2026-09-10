# Security Policy

CYBERVOYRAX Workspace is a deliberately vulnerable web application created for cybersecurity education, authorized penetration testing, and security training.

## Safe Use

CYBERVOYRAX Workspace must only be deployed in a controlled environment.

Recommended environments include:

- A local computer
- An isolated virtual machine
- A private lab network
- A dedicated cybersecurity training environment

Do not expose CYBERVOYRAX Workspace directly to the public internet.

Do not store real passwords, personal information, confidential company information, production credentials, API keys, customer data, or other sensitive information inside the application.

Only test systems that you own or have explicit authorization to assess.

## Intended Vulnerabilities

Some security weaknesses in CYBERVOYRAX Workspace are intentionally included as part of the training environment.

The public repository does not document the location, parameters, payloads, exploit paths, or complete inventory of those vulnerabilities in order to preserve the intended black-box assessment experience.

Intentionally planted training vulnerabilities do not need to be reported as security issues.

## Reporting Accidental Security Issues

If you discover a vulnerability that appears to be outside the intended training design, especially one that could affect the host system, Docker environment, installation process, repository secrets, or other systems outside the CYBERVOYRAX application boundary, please report it privately to the maintainer rather than publishing exploitation details immediately.

Maintainer:

Praise Testimony — CYBERVOYRAX

GitHub:
https://github.com/dhboss-p

LinkedIn:
https://linkedin.com/in/praise-testimony-cybervoyrax

## Assessment Credentials

The default assessment account is provisioned locally during installation.

Generated credentials are stored in:

`.lab-credentials`

This file is intentionally excluded from version control and must not be committed to the repository.

## Disclaimer

CYBERVOYRAX Workspace is provided strictly for educational purposes and authorized security testing.

Users are responsible for ensuring that their testing activities comply with applicable laws, policies, and authorization requirements.
