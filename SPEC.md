# Product specification — SentinelOps

> Status: approved through Genesis. Product implementation remains blocked until the Genesis plan is explicitly approved.

## Problem

Developers and site-reliability engineers need a safe way to build, test, and
evaluate incident-response automation before granting it access to a real
system. Typical demos are tied to one hard-coded failure, lack trustworthy
telemetry, and cannot prove that a proposed remediation was safe or effective.

SentinelOps will provide a local, disposable application plus reproducible
failure scenarios. It will collect operational evidence, coordinate an
evidence-backed investigation, require human approval before any mutation,
apply a narrowly allowlisted remediation, and verify recovery. The first
release must prove this workflow locally while keeping integration-specific
code behind clear module boundaries so external projects can be supported
later.

## Users

- Primary user: a developer or SRE learning, developing, or evaluating
  automated incident response on a local machine.
- Secondary user: a platform team assessing whether SentinelOps can later be
  connected to an existing staging or production environment.
- Affected systems: only the disposable local application in this release.

## Terminology

- A failure scenario has an `SCN-*` identifier and deliberately changes the
  disposable application so a known fault can be tested.
- An alert is a monitoring-system notification that an observed condition has
  crossed a configured threshold.
- An incident has an `INC-*` identifier and is created or updated by SentinelOps
  after it accepts an alert. A failure scenario is not itself an incident.

## Functional requirements

- FR-1: The user can start, inspect, and stop a healthy disposable application
  composed of an API gateway, orders service, payments service, PostgreSQL, and
  Redis using documented local commands.
- FR-2: The system provides a versioned failure-scenario format containing an
  identifier, trigger, expected symptoms, known root cause, permitted
  remediation, verification procedure, and cleanup procedure.
- FR-3: The user can trigger, inspect, and reset one selected failure scenario
  without rebuilding the entire application.
- FR-4: The initial failure-scenario catalog contains `SCN-001` faulty payments
  deployment, `SCN-002` database connection exhaustion, and `SCN-003` Redis
  unavailability; implementation may deliver them incrementally in that order.
- FR-5: Failure scenarios run sequentially by default and restore the
  application to a verified healthy baseline before another scenario begins.
- FR-6: The application emits structured logs, metrics, traces, health data,
  and deployment events through OpenTelemetry-compatible local tooling.
- FR-7: SentinelOps records an incident timeline containing the originating
  alert, observations, hypotheses, supporting or contradicting evidence,
  decisions, approvals, actions, and verification results.
- FR-8: A triage step identifies the affected service and severity, and an
  investigation step queries available telemetry and deployment information.
- FR-9: A diagnosis identifies a probable root cause, confidence, cited
  evidence, alternative hypotheses, and missing information; unsupported
  conclusions must not be presented as facts.
- FR-10: SentinelOps proposes only remediation actions declared by the active
  failure scenario and presents their expected scope and risk for review.
- FR-11: Every state-changing remediation requires an explicit human approval
  associated with the incident and proposed action.
- FR-12: After approval, SentinelOps can execute an allowlisted remediation,
  verify service recovery, and report failure without silently retrying a
  potentially duplicated side effect.
- FR-13: The incident workflow persists enough state to resume after the
  SentinelOps worker restarts while avoiding duplicate remediation.
- FR-14: A replayable evaluation suite measures diagnosis correctness, time to
  diagnosis, remediation success, blocked unsafe actions, and model cost for
  the failure-scenario catalog.
- FR-15: Automated tests can use recorded or deterministic model responses so
  routine validation does not require paid API calls.
- FR-16: Local telemetry, runtime, deployment, and remediation access remain in
  separate modules from agent reasoning so a future integration can replace a
  local module without rewriting the investigation workflow.
- FR-17: Prometheus collects application metrics and evaluates versioned alert
  rules; firing alerts are routed through Alertmanager.
- FR-18: Alertmanager delivers firing and resolved notifications to a
  SentinelOps HTTP webhook using a documented alert payload contract.
- FR-19: SentinelOps validates each webhook, deduplicates it by alert
  fingerprint, creates or updates an `INC-*` incident, and starts investigation
  only for an accepted firing alert.

## Non-functional requirements

- NFR-1: The release must not require or accept access to real production
  infrastructure; all mutations are confined to the documented disposable
  local environment.
- NFR-2: Each failure-scenario trigger and cleanup must complete successfully in
  five consecutive automated runs from a healthy baseline.
- NFR-3: An automated safety test must prove that every state-changing action
  is rejected when approval is missing, expired, or for a different incident.
- NFR-4: Secrets and LLM credentials must be read from the environment, must not
  appear in logs or incident records, and must not be committed to the
  repository.
- NFR-5: Every diagnosis shown to a user must link to locally retained evidence
  or clearly label the statement as a hypothesis.
- NFR-6: The complete local stack should start within five minutes on a machine
  with 8 CPU cores, 16 GB RAM, and 40 GB free storage after images and
  dependencies have been downloaded.
- NFR-7: Paid model use must expose per-incident token and estimated cost data,
  and the application must support a configurable per-incident request limit.
- NFR-8: Local workflow and incident state must survive an ordinary process
  restart without losing an approval decision or executing an approved action
  more than once.
- NFR-9: Repeated deliveries of the same active alert fingerprint must not
  create duplicate incidents, and invalid webhook payloads must produce no
  incident.

## Constraints

- The first runtime is Docker Compose on the local developer machine.
- Python 3.12 and FastAPI are the initial application and control-plane stack.
- OpenTelemetry-compatible open-source components provide local telemetry;
  Prometheus evaluates local metric alert rules and Alertmanager routes alerts.
- Temporal's local development runtime may be introduced only when durable
  workflows are implemented; it is not required for the first incident slice.
- An LLM API key is not required for the incident lab or deterministic tests.
- Initial paid model usage should fit within a user-controlled budget of
  approximately INR 500-1,000.
- The local implementation must stay simple: module boundaries are required,
  but a dynamic plugin framework is not.

## Non-goals

- Connecting to Datadog, CloudWatch, PagerDuty, GitHub, Kubernetes, or other
  external systems.
- Operating on a real production environment.
- Performing unattended or unrestricted remediation.
- Supporting multiple tenants, billing, or a hosted SaaS control plane.
- Running compound or simultaneous incidents; those follow validated
  single-incident scenarios.
- Providing a polished web dashboard before the command and API workflow is
  proven.
- Supporting multiple LLM providers in the initial release.
- Automatically authoring or changing monitoring alert rules; alert rules are
  version-controlled project configuration reviewed by a human.

## Acceptance criteria

- AC-1: A documented command starts the complete application, and an automated
  health check proves that gateway, orders, payments, PostgreSQL, and Redis are
  healthy.
- AC-2: For every scenario in the initial catalog, an automated check can
  trigger the expected symptoms, confirm the known root cause is present, run
  cleanup, and prove the healthy baseline in five consecutive runs.
- AC-3: After an incident is created, an automated check can retrieve correlated
  logs, metrics, traces, health information, and the relevant deployment or
  runtime change from the local telemetry stack.
- AC-4: Against the fixed evaluation suite, SentinelOps identifies the expected
  root cause with cited supporting evidence in at least 80 percent of runs and
  does not mark unsupported statements as verified facts.
- AC-5: An automated integration test proves that remediation without a valid
  matching approval performs no state-changing operation.
- AC-6: For the faulty-deployment scenario, an approved rollback restores the
  healthy payments version and the verification check observes recovery.
- AC-7: Terminating and restarting the SentinelOps worker after approval does
  not lose workflow state and does not execute the remediation more than once.
- AC-8: The full automated suite can run with recorded model responses and no
  LLM API key.
- AC-9: A fresh developer can follow the documented setup and complete start,
  scenario trigger, incident inspection, reset, and stop without editing source
  code.
- AC-10: Triggering `SCN-001` causes real payment failures, Prometheus fires the
  configured alert, Alertmanager posts it to SentinelOps, and SentinelOps
  creates one `INC-*` incident without a manually submitted alert.
- AC-11: Replaying the same alert fingerprint updates the existing incident,
  while an invalid webhook payload is rejected and creates no incident.

## Risks

- Agents may overfit to known scenarios. Mitigation: keep scenario truth hidden
  from investigation inputs and add holdout variations to evaluation.
- Model output may hallucinate a root cause. Mitigation: require evidence-linked
  findings, preserve alternative hypotheses, and measure diagnosis accuracy.
- A remediation may worsen an incident or execute twice. Mitigation: use a
  strict allowlist, matching human approval, idempotency keys, and post-action
  verification.
- Fault injection may leave the environment unhealthy. Mitigation: provide
  scenario-specific cleanup plus a complete baseline reset and verification.
- Local infrastructure may consume excessive resources. Mitigation: start with
  Docker Compose, limit service resources, and defer Kubernetes and a polished
  dashboard.
- LLM tests may become expensive or nondeterministic. Mitigation: use recorded
  responses for routine checks and enforce per-incident request limits.
- Alert retries or alert storms may create duplicate investigations. Mitigation:
  validate the webhook contract and deduplicate by alert fingerprint before
  creating an incident.

## Open questions

- None for specification approval. The exact hosted model and any future first
  external connector will be selected only when their approved implementation
  tasks begin.
