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