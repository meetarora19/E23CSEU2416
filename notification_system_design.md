# Campus Notification System Architecture

## Stage 1

**Primary System Actions:**
1. Retrieve a paginated list of notifications for the authenticated student.
2. Update the status of a specific notification to "viewed".
3. Bulk update all pending notifications to "viewed".
4. Stream live notification alerts to the client interface.

**RESTful API Contracts:**

### 1. Retrieve User Notifications
* **Endpoint:** `GET /api/v1/student/notifications`
* **Headers:** `Authorization: Bearer <access_token>`
* **Query Parameters:** `size` (limit), `page`, `category` (Event/Result/Placement)
* **Response (Status 200):**
{
  "success": true,
  "results": [
    {
      "notificationId": "a1b2c3d4-e5f6-7890",
      "category": "Placement",
      "content": "Upcoming campus drive for Tech Solutions Inc.",
      "readStatus": false,
      "createdAt": "2026-05-11T14:30:00Z"
    }
  ],
  "pagination": { "currentPage": 1, "totalPages": 5 }
}

### 2. Update Single Notification Status
* **Endpoint:** `PATCH /api/v1/student/notifications/{notificationId}`
* **Headers:** `Authorization: Bearer <access_token>`
* **Request Payload:**
{
  "readStatus": true
}
* **Response (Status 200):**
{
  "success": true,
  "message": "Status updated successfully"
}

### 3. Acknowledge All Notifications
* **Endpoint:** `POST /api/v1/student/notifications/acknowledge-all`
* **Headers:** `Authorization: Bearer <access_token>`
* **Response (Status 200):**
{
  "success": true,
  "message": "All unread notifications cleared"
}

**Real-Time Architecture Design:**
To achieve live updates without overwhelming the server with constant client polling, I recommend utilizing **Server-Sent Events (SSE)**. Unlike WebSockets, which provide a heavy two-way communication channel, SSE is specifically optimized for one-directional event streaming (Server to Client). This makes it highly efficient for a notification feed, requiring less server overhead while offering built-in browser reconnection capabilities.

---

## Stage 2

**Database Recommendation:** **PostgreSQL**
**Justification:** A campus alert system handles highly structured data that requires strong relational links (e.g., linking a notification to a specific student ID). PostgreSQL provides excellent ACID compliance to ensure data integrity and supports advanced indexing mechanisms which are crucial for performance as the application grows.

**Proposed SQL Schema:**
```sql
CREATE TABLE app_notifications (
    record_id UUID PRIMARY KEY,
    recipient_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    is_viewed BOOLEAN DEFAULT FALSE,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Anticipated Scaling Challenges & Mitigation:**
* **The Bottleneck:** As the table grows to millions of rows, querying for a student's unread notifications on every single page load will severely degrade database performance.
* **Mitigation 1 (Database Level):** Create a composite index on `(recipient_id, is_viewed, created_on)` to dramatically speed up the standard "fetch unread" queries.
* **Mitigation 2 (Application Level):** Implement an in-memory cache like **Redis**. We can cache the total "unread count" for active sessions, preventing the system from hitting the main PostgreSQL database every time a student navigates to a new page.
* **Mitigation 3 (Storage Level):** Utilize table partitioning. We can partition the data by semester or month, archiving older notifications to keep the active table lightweight.

**Core SQL Queries (Based on Stage 1):**
```sql
-- Retrieve paginated notifications for a specific user
SELECT * FROM app_notifications 
WHERE recipient_id = 1042 
ORDER BY created_on DESC 
LIMIT 10 OFFSET 0;

-- Acknowledge a specific notification
UPDATE app_notifications 
SET is_viewed = TRUE 
WHERE record_id = 'a1b2c3d4-e5f6-7890' AND recipient_id = 1042;
```

---

## Stage 3

**1. Query Accuracy and Performance Bottleneck:**
The provided query (`SELECT * FROM notifications WHERE studentID = 1042 AND isRead = false ORDER BY createdAt ASC;`) is logically accurate for fetching unread notifications. However, it is performing extremely slowly because it relies on a **Full Table Scan**. Since there are 5,000,000 notifications and no relevant indexes, the database engine is forced to inspect every single row sequentially to find the matching records for student `1042`.

**2. Proposed Optimization and Computation Cost:**
I would implement a composite B-Tree index on the columns `(studentID, isRead, createdAt)`. 
* **Current Computation Cost:** $O(N)$, where $N$ is the total number of rows in the table.
* **Optimized Computation Cost:** $O(\log N)$ to traverse the index tree, followed by $O(K)$ to fetch the $K$ matching rows. This will drastically reduce query execution time.

**3. Evaluating "Index Every Column" Advice:**
Adding an index to every column is **highly ineffective and counterproductive**. 
* **Storage Bloat:** Indexes consume significant disk space.
* **Write Degradation:** Every time a new notification is inserted (which happens frequently), every single index must be updated. This creates a massive performance penalty on write operations (`INSERT`, `UPDATE`, `DELETE`). Indexes should only be strategically applied to columns used frequently in `WHERE`, `ORDER BY`, or `JOIN` clauses.

**4. Recent Placement Notifications Query:**
```sql
SELECT studentID
FROM notifications
WHERE notificationType = 'Placement'
    AND createdAt >= NOW() - INTERVAL '7 days';
```


---

## Stage 4

**The Bottleneck:**
Fetching notifications from the primary database on every single page load for 50,000+ students creates an unsustainable number of read operations. This overwhelms database connections and severely degrades the user experience.

**Proposed Performance Strategies & Tradeoffs:**

**1. In-Memory Server Caching (Redis)**
Instead of querying PostgreSQL on every page navigation, we store the recent notifications payload and the "unread count" for active users in a Redis cache. The API serves the data directly from RAM.
* **Pros:** Blazing fast read times (sub-millisecond); massively protects the primary database from read-heavy traffic.
* **Tradeoffs:** Increases infrastructure complexity and costs. Requires careful "cache invalidation" logic (e.g., when a student reads a message, we must instantly update the cache so they don't see stale, outdated data).

**2. Global Frontend State & Server-Sent Events (SSE)**
We change the frontend behavior. The client fetches the notifications *once* upon logging in and stores them in a global state manager (like React Context or Redux). As the user navigates between pages, the UI reads from the local state, making zero new API calls. New alerts are pushed silently to this state via SSE.
* **Pros:** Eliminates 90% of repetitive API calls; creates a buttery-smooth, instant UI experience.
* **Tradeoffs:** The server must maintain thousands of open SSE connections simultaneously. If the user refreshes the browser tab entirely, the state is wiped and a fresh DB fetch is required.

**3. HTTP Caching Mechanisms (ETags)**
The server sends an `ETag` (a unique hash of the inbox state) with the notifications. On the next page load, the browser sends that ETag back. If no new notifications exist, the API simply returns a `304 Not Modified` status without querying the database.
* **Pros:** Very easy to implement; uses standard built-in browser features.
* **Tradeoffs:** The client still has to make an HTTP request over the network for validation, so it doesn't completely eliminate server traffic like the Global State approach does.


---

## Stage 5

**1. Shortcomings of the Proposed Implementation:**
* **Synchronous & Blocking Execution:** The `for` loop executes sequentially. Network calls like `send_email()` are incredibly slow. If one email takes just 0.5 seconds, processing 50,000 students will take almost 7 hours. The server's HTTP request will time out long before it finishes.
* **Tight Coupling & Zero Fault Tolerance:** Database insertion, email, and app pushes are tightly linked. If the email provider API goes down (causing the failure for the 200 students in the logs), it crashes the entire execution loop. 
* **The "Midway Failure" Disaster:** Because it crashed midway, the remaining thousands of students got nothing. Re-running the script naively to reach the rest would result in duplicate emails for the first batch. There is no built-in retry mechanism.

**2. Should saving to DB and sending email happen together?**
**No, they must be decoupled.** * The database insert is a critical system record. It should happen instantly in one single, fast database transaction (a Bulk Insert).
* Sending an email is a secondary, slow, third-party network operation. It should happen entirely asynchronously in the background.

**3. Reliable & Fast Redesign Strategy:**
I would implement an **Event-Driven Architecture** using a Message Queue (like RabbitMQ, AWS SQS, or Redis with BullMQ) and separate background worker servers. The main API just saves the data and drops jobs into a queue, responding to the HR user instantly.

**Revised Pseudocode:**
```python
function notify_all(student_ids_array, message_string):
    # 1. BULK INSERT to Database (Blazing fast, single transaction)
    try:
        db.bulk_insert_notifications(student_ids_array, message_string)
    except Exception as e:
        return "Critical Error: Failed to save to DB."

    # 2. Push tasks to a Message Queue (Extremely fast, non-blocking)
    for student_id in student_ids_array:
        message_queue.enqueue(
            queue_name="email_queue", 
            payload={"id": student_id, "msg": message_string}
        )
        message_queue.enqueue(
            queue_name="app_push_queue", 
            payload={"id": student_id, "msg": message_string}
        )
    
    # HR gets an instant success response on their screen
    return "Notifications queued and processing in the background."

# Background Worker Process (Runs on entirely separate servers)
function process_email_job(job_data):
    try:
        send_email(job_data.id, job_data.msg)
    except EmailServiceError:
        # Message queues automatically catch errors and retry failed jobs
        message_queue.retry_later(job_data)
```