# Lab 8: GraphQL Alongside REST

## 📊 REST vs. GraphQL Comparison (My Courses Screen)

| Metric | REST (Multi-request) | GraphQL (Single-request) |
| :--- | :--- | :--- |
| **Number of HTTP Requests** | 5 requests | 1 request |
| **Network Roundtrips** | 2 rounds (Sequential) | 1 round (Single pass) |
| **Payload Size** | ~1145 bytes | ~339 bytes |
| **Database SQL Queries** | 6 queries | 3 queries (via DataLoader) |

---

## 🧪 Experiment Results

1. **Experiment 1 (Field Typo):** Sending a GraphQL query with a non-existent field (`titel`) returns an HTTP status of `200 OK` with the error description contained in the `errors` payload, whereas REST returns a standard `400/422` error code[cite: 13].
2. **Experiment 2 (Null Propagation):** Removing `| None` from a required relationship field in the schema causes the entire parent object in `data` to nullify if a requested record is missing, due to GraphQL's strict null-propagation rule[cite: 16, 17].
3. **Experiment 3 (Mutations via GET):** Attempting to execute a `likeCourse` mutation using an HTTP GET method is blocked by the router with a standard `400 Bad Request` status[cite: 20].
4. **Experiment 4 (N+1 Problem & Resolution):** Without `DataLoader`, nested relationship resolvers trigger a cascading number of SQL queries ($N+1$)[cite: 21, 24, 25]. Implementing batch loaders reduces database queries to a fixed $3$ queries regardless of related data volume[cite: 27, 28].
5. **Experiment 5 (Server Protection):** 
   - `QueryDepthLimiter(max_depth=5)` successfully blocks deep recursive cycles[cite: 34, 35].
   - `MaxAliasesLimiter(max_alias_count=10)` prevents alias overloading attacks[cite: 34, 35].
   - `MaskErrors` hides internal database exceptions (such as SQLAlchemy/PostgreSQL stack traces), replacing them with a safe `"Unexpected error."` message[cite: 33, 35].

---

## 🚀 Bonus Tasks

### Task 1: Validation Errors as Problem Details
- **Implementation:** Added a `RequestValidationError` exception handler in `problem.py` (`install`) so FastAPI validation failures return `422 Unprocessable Entity` with `Content-Type: application/problem+json` and `type: "https://example.com/problems/validation-error"`[cite: 53, 54].
- **Where the handler gets the error list:** FastAPI passes `RequestValidationError` to the handler, and `exc.errors()` provides a list of dictionaries containing `loc` (location tuple, e.g. `("body", "name")`) and `msg` (validation message), which are mapped into `{"in": ..., "field": ..., "detail": ...}` objects[cite: 53, 54].
- **Why `errors` is an extension field:** RFC 9457 defines five core members (`type`, `title`, `status`, `detail`, `instance`) and explicitly allows custom extension members[cite: 4, 5, 53]. Including `errors` keeps the response strictly RFC 9457-compliant while delivering all field-level validation issues in one payload[cite: 53, 54].

### Task 2: `createStudent` Mutation and Shared Domain Rules
- **Implementation:** Added whitespace-trimmed length validation (`len(name.strip()) < 2`) in `services.create_student` raising `ServiceError("INVALID_NAME", ...)`, mapped `"INVALID_NAME"` to `422` (`invalid-name`) in `problem.py`, and exposed the `createStudent` mutation in `graphql_api.py` returning `CreateStudentPayload` with `userErrors`[cite: 54, 55, 56].
- **Why the rule lives in `services.py`:** Placing business validation in the services layer ensures a single source of truth—both REST (`POST /students`) and GraphQL (`createStudent`) enforce the exact same rule consistently without duplicating validation logic[cite: 3, 54, 56].
- **Avoiding `500 Internal Server Error` on new error codes:** Whenever a new `ServiceError` code is added in `services.py`, its HTTP status, `type` slug, and `title` must also be registered in the `PROBLEMS` dictionary in `problem.py`; otherwise, `on_service_error` triggers a `KeyError` and FastAPI falls back to an unhandled `500 Internal Server Error` on REST endpoints[cite: 5, 56].

### Task 3: Blocking Resolver vs. Threadpool
To launch: uvicorn blocking_app:app --port 8001
- **Results (4 concurrent requests with `SELECT pg_sleep(0.5)` on port 8001):**
  - `REST, def route`: ~0.53 s[cite: 58]
  - `GraphQL, sync resolver`: ~2.02 s[cite: 58]
  - `GraphQL, async + run_in_threadpool`: ~0.52 s[cite: 58]
- **Explanation:** FastAPI automatically dispatches synchronous `def` routes to an external thread pool so they do not block the main `asyncio` event loop[cite: 58]. In contrast, Strawberry executes synchronous resolvers directly on the event loop thread, serializing the four 0.5 s database waits into ~2.0 s[cite: 58]. In `blocking_app.py`, the difference is visible in `slow_threadpool`, which uses `await run_in_threadpool(pause, info.context.db)` to offload the blocking call to a worker thread[cite: 57, 58]. In our catalog API, queries take only a few milliseconds so blocking is unnoticeable, but under high concurrency or slow database queries, synchronous resolvers become a severe bottleneck[cite: 27, 58].