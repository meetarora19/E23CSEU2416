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