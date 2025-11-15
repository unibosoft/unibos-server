# Phase 3: Platform Infrastructure - TODO

**Status**: Foundation Only - Implementation Deferred
**Created**: 2025-11-12
**Priority**: P2 (After Phase 2.3 module migration)

## Overview

Phase 3 involves building distributed system infrastructure for UNIBOS. Currently only the directory structure exists. Full implementation will happen after core functionality is stable.

## Current State

```
core/platform/
├── orchestration/  (empty - task distribution)
├── routing/        (empty - connection routing)
└── offline/        (empty - offline mode)
```

## 1. Task Distribution System (Orchestration)

**Goal**: Enable Rocksteady (VPS) to distribute tasks to Raspberry Pi workers

### Components to Build

#### `core/platform/orchestration/task_queue.py`
- Celery-based task queue setup
- Redis backend configuration
- Task serialization/deserialization
- Priority queue support

#### `core/platform/orchestration/task_distributor.py`
- Task routing logic
- Worker capacity management
- Task retry mechanisms
- Dead letter queue handling

#### `core/platform/orchestration/task_scheduler.py`
- Cron-like scheduling
- Recurring task management
- Task dependencies
- Scheduled task persistence

#### `core/platform/orchestration/worker_registry.py`
- Worker registration/deregistration
- Worker heartbeat monitoring
- Capability declaration (what tasks each worker can handle)
- Worker load tracking

#### `core/platform/orchestration/health_monitor.py`
- Worker health checks
- Task execution monitoring
- Performance metrics collection
- Alert system for failures

### Technology Stack
- **Celery** 5.2+ (already in requirements.txt)
- **Redis** 4.0+ (already in requirements.txt)
- **Kombu** for messaging
- **Flower** for monitoring (optional)

### Implementation Steps
1. Design task types and schemas
2. Implement basic queue with Celery
3. Add worker registration
4. Implement health monitoring
5. Add retry logic and error handling
6. Test with Raspberry Pi worker

### Testing Requirements
- Unit tests for each component
- Integration tests with Redis
- Load testing with multiple workers
- Failover testing (worker dies mid-task)

---

## 2. Connection Routing

**Goal**: Smart routing of requests to appropriate endpoints (local raspberry vs VPS)

### Components to Build

#### `core/platform/routing/router.py`
- Main routing decision engine
- Request classification
- Endpoint selection algorithm
- Fallback mechanisms

#### `core/platform/routing/priority_table.py`
- Configurable routing priorities
- Rule-based routing (by module, user, location)
- Dynamic priority updates
- Priority persistence

#### `core/platform/routing/load_balancer.py`
- Round-robin distribution
- Weighted distribution (by server capacity)
- Least-connections algorithm
- Sticky sessions (when needed)

#### `core/platform/routing/health_checker.py`
- Periodic health checks to all endpoints
- Response time tracking
- Availability status
- Circuit breaker pattern

### Routing Policies to Implement

#### `core/platform/routing/policies/local_first.py`
```python
# Prefer local raspberry if available
# Fallback to VPS if local unavailable
```

#### `core/platform/routing/policies/performance_based.py`
```python
# Route based on latency and load
# Dynamic optimization
```

#### `core/platform/routing/policies/cost_optimized.py`
```python
# Minimize bandwidth costs
# Prefer local for large files
```

### Implementation Steps
1. Design routing decision tree
2. Implement health checker
3. Build basic router with fallback
4. Add load balancer
5. Implement routing policies
6. Add metrics and monitoring

### Testing Requirements
- Test each routing policy
- Failover scenarios (endpoint goes down)
- Load testing with concurrent requests
- Latency measurements

---

## 3. Offline Mode Strategy

**Goal**: Enable full functionality when disconnected from internet/VPS

### Components to Build

#### `core/platform/offline/offline_detector.py`
- Network connectivity detection
- Periodic connection checks
- State management (online/offline)
- Event triggers on state change

#### `core/platform/offline/sync_strategy.py`
- Sync queue management
- Conflict detection
- Merge strategies
- Bandwidth-aware syncing

#### `core/platform/offline/conflict_resolver.py`
- CRDT (Conflict-free Replicated Data Types) implementation
- Last-write-wins (LWW) for simple cases
- Three-way merge for complex cases
- User-initiated conflict resolution UI

#### `core/platform/offline/queue_manager.py`
- Operation queue (CRUD operations during offline)
- Queue persistence (survive restarts)
- Queue replay on reconnection
- Failed operation handling

#### `core/platform/offline/storage/local_cache.py`
- Local data caching
- Cache invalidation
- Cache size management
- Partial sync support

#### `core/platform/offline/storage/delta_tracker.py`
- Track changes made locally
- Delta generation
- Delta compression
- Delta application

### CRDT Implementation
- Use **Automerge** or **Yjs** libraries
- Implement for key data types:
  - Documents
  - User profiles
  - Shared lists
  - Configuration

### Implementation Steps
1. Research CRDT libraries (Automerge, Yjs)
2. Design offline-first data models
3. Implement offline detector
4. Build operation queue
5. Implement basic sync
6. Add conflict resolution
7. Test with real disconnect scenarios

### Testing Requirements
- Offline operation tests
- Reconnection and sync tests
- Conflict scenarios (same data edited in 2 places)
- Data integrity verification
- Performance testing (large sync backlogs)

---

## Integration Points

### With Django
- Middleware for routing decisions
- Background tasks via Celery
- Offline queue integrated with ORM

### With Mobile (Birlikteyiz Flutter)
- Offline-first local database (Hive/Isar)
- Sync API endpoints
- Push notifications for conflicts

### With Raspberry Pi
- Worker daemon for task execution
- Local data cache
- Health reporting to VPS

---

## Dependencies

### Python Packages
```txt
# Already in requirements.txt
celery>=5.2.0
redis>=4.0.0

# Need to add
flower>=1.2.0          # Celery monitoring
automerge-py>=0.1.0    # CRDT library (if available)
watchdog>=2.1.0        # File system events
```

### System Requirements
- Redis server (for Celery)
- PostgreSQL with replication (for Raspberry Pi)
- Network connectivity monitoring tools

---

## Deployment Considerations

### Rocksteady (VPS)
- Celery worker pool (for heavy tasks)
- Redis instance
- Task scheduler
- Monitoring dashboard

### Raspberry Pi
- Celery worker (lightweight tasks)
- Local PostgreSQL replica
- Offline cache
- mDNS service for local discovery

### Local Development
- Docker Compose for testing distributed setup
- Multiple worker simulation
- Network throttling for offline testing

---

## Success Metrics

1. **Task Distribution**
   - Task completion rate: >99%
   - Average task latency: <500ms
   - Worker utilization: 60-80%

2. **Routing**
   - Routing decision time: <10ms
   - Correct endpoint selection: >99%
   - Failover time: <1s

3. **Offline Mode**
   - Offline operation success: 100%
   - Sync conflicts: <1%
   - Data loss: 0%
   - Sync time: <30s for typical usage

---

## Timeline Estimate

- **Task Distribution**: 2 weeks
- **Connection Routing**: 1 week
- **Offline Mode**: 3 weeks (most complex)
- **Integration & Testing**: 1 week
- **Total**: ~7 weeks (flexible)

---

## Notes

- This is infrastructure work, not user-facing features
- Can be done incrementally (task distribution first)
- Requires multi-device testing environment
- Offline mode is the most complex piece
- Consider hiring for CRDT expertise if needed

---

**Next Steps**:
1. Complete Phase 2.3 (module migration)
2. Get web UI working end-to-end
3. Then revisit Phase 3 implementation

**Document Version**: 1.0
**Last Updated**: 2025-11-12
