# SentinelOps

SentinelOps is a local-first environment for developing and evaluating safe,
evidence-backed incident-response automation.

The repository uses a Genesis specification-first workflow. The healthy local
application foundation is the first implementation slice.

## Project documents

- [Product specification](SPEC.md)
- [Architecture diagram](docs/architecture.md)
- [Genesis implementation plan](.genesis/PLAN.md)

## Initial scope

- Disposable Docker Compose application
- Reproducible `SCN-*` failure scenarios
- Prometheus alert evaluation and Alertmanager webhook delivery
- SentinelOps-managed `INC-*` incident records
- OpenTelemetry-compatible evidence
- Evidence-backed diagnosis
- Human-approved, allowlisted remediation
- Replayable safety and accuracy evaluation

External production connectors and unattended remediation are deliberately
outside the initial release.

## Run the healthy local stack

Prerequisites: Docker with Compose and Python 3.12.

```bash
make start
make status
make verify
make stop
```

`make start` builds and starts the API gateway, orders service, payments
service, PostgreSQL, and Redis. Only the gateway is exposed to the host, at
`http://127.0.0.1:8000`. Each application health check verifies its downstream
dependencies, and `make verify` confirms all five containers are healthy.

## Local incident flow

```text
Failure scenario -> Application failure -> Prometheus alert
-> Alertmanager webhook -> SentinelOps incident -> Investigation
```

A failure scenario and an incident are deliberately different: `SCN-001`
injects a known local fault, while SentinelOps creates an `INC-*` record only
after it accepts the resulting alert.
