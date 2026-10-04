# FABRIC Ops V1 Data Model

## users
id UUID PK
name text
email text UNIQUE
role enum(admin, lead, member)
created_at timestamp

## events
id UUID PK
name text
description text nullable
status enum(draft, planned, active, completed, cancelled)
start_at timestamp nullable
end_at timestamp nullable
created_by UUID → users.id
created_at timestamp
updated_at timestamp

## teams
id UUID PK
event_id UUID → events.id
name text
created_at timestamp
UNIQUE(event_id, name)

## team_members
team_id UUID → teams.id
user_id UUID → users.id
joined_at timestamp
PRIMARY KEY(team_id, user_id)

## tasks
id UUID PK
team_id UUID → teams.id
title text
description text nullable
assigned_to UUID → users.id
priority enum(low, medium, high)
status enum(todo, in_progress, submitted, approved, rejected)
due_at timestamp nullable
created_by UUID → users.id
created_at timestamp
updated_at timestamp

## submissions
id UUID PK
task_id UUID → tasks.id
submitted_by UUID → users.id
content text
status enum(pending, approved, rejected)
reviewed_by UUID → users.id nullable
reviewed_at timestamp nullable
created_at timestamp

## audit_logs
id UUID PK
actor_id UUID → users.id
action text
entity_type text
entity_id UUID
metadata JSONB nullable
created_at timestamp

## Relationships
User ──< TeamMember >── Team ──> Event
User ──> Task (assignment)
User ──> Submission (submit/review)
Team ──< Task ──< Submission
