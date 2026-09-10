# CYBERVOYRAX Database

Phase 2 introduces the first full application schema and deterministic seed world.

## Tables

- app_meta
- roles
- departments
- users
- projects
- project_members
- project_comments
- documents
- activity_logs
- password_reset_tokens
- user_sessions

## Seed policy

The Phase 2 seed engine is deterministic and contains fictional data only.

Password values are not stored in the database. Seed passwords are converted to bcrypt hashes before insertion.

The Phase 2 seed is development-oriented. Running the seed script resets seed-owned tables. Later phases will transition to migration-safe data handling where appropriate.
