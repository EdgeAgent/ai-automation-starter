# Security policy

This repository is a Python dependency starter kit and does not itself operate a hosted service.

## Reporting a vulnerability

Please do not publish exploit details in a public issue. Use GitHub's private vulnerability reporting feature for this repository if it is enabled. Otherwise, contact the repository maintainer privately and provide the affected profile/package, Python and platform details, impact, and reproduction steps. Avoid including credentials, private data, or live exploit payloads.

## Dependency and deployment safety

- Review and test dependency update proposals before merging or deploying them.
- For deployed applications, create and maintain an application-specific lock file.
- Keep API keys and service credentials in a secret manager or protected environment variables; never commit them.
- Treat downloaded documents, model output, and scraped content as untrusted input.
- Deploy APIs behind appropriate authentication, authorization, rate limits, TLS, and monitoring.
