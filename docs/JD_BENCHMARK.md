# Real SWE JD Benchmark

Benchmarked against scraped public postings:

- Sezzle Senior Software Engineer: Go, React, REST APIs, distributed/cloud architecture, LLM tools, SQL, observability, CI/CD, Kubernetes on AWS.
- Integrate Backend Engineer: distributed backend systems, Go/Python, gRPC, REST/JSON APIs, PostgreSQL/NoSQL, Kubernetes, Terraform, cloud infrastructure.
- Qdrant Senior Platform Engineer: Go/Python automation, Kubernetes automation, cloud infrastructure, observability, Linux/networking, Terraform.

Sources fetched during validation:

- https://job-boards.greenhouse.io/sezzle/jobs/6570434003
- https://jobs.lever.co/integrate/aa55db97-371d-4378-bc88-0c058539190b
- https://jobs.ashbyhq.com/qdrant.tech/0a8df73a-3ff8-456f-8ce0-f5195fde8579

## Results

| Posting | Skills changed | Bullet lines changed | Examples |
| --- | ---: | ---: | --- |
| Sezzle Senior SWE | 2 | 8 | `REST`, `CI/CD`, `Kubernetes-backed distributed backend services`, `REST APIs` |
| Integrate Backend Engineer | 1 | 6 | `REST`, `Kubernetes-backed distributed backend services`, `REST API requests` |
| Qdrant Platform Engineer | 0 | 4 | `developer tooling and automation`, `Kubernetes-backed backend services` |

## Guardrail check

Allowed automatic bullet edits are technology qualifiers on existing work only:

- `APIs` -> `REST APIs`
- `API backend` -> `REST API backend`
- `backend services in Go` -> `Kubernetes-backed backend services in Go`
- `backend services in Go` -> `Kubernetes-backed distributed backend services in Go`
- `developer tooling` -> `developer tooling and automation`
- `Shipped well-tested...` -> `Shipped CI/CD-ready, well-tested...`

Still suggestion-only because they would be new claims:

- Terraform
- gRPC
- Linux/networking
- Redis
- GraphQL
- queue systems such as Kafka/SQS/RabbitMQ

## Verdict

The update is now substantial for backend/platform JDs while staying conservative: it changes 2-4 existing bullets for matching roles, preserves bullet actions/results, and leaves unproven technologies as suggestions.
