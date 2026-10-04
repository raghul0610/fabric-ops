export type Role = "ADMIN" | "LEAD" | "MEMBER";
export type EventState = "DRAFT" | "PLANNED" | "ACTIVE" | "COMPLETED" | "CANCELLED";
export type TaskState = "TODO" | "IN_PROGRESS" | "SUBMITTED" | "APPROVED" | "REJECTED";

export interface Event {
  id: string;
  name: string;
  description: string | null;
  state: EventState;
  starts_at: string;
  ends_at: string;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: string;
  event_id: string;
  name: string;
  created_at: string;
}

export interface TeamMember {
  team_id: string;
  user_id: string;
  membership_role: "LEAD" | "MEMBER";
  created_at: string;
}

export interface Task {
  id: string;
  event_id: string;
  team_id: string;
  title: string;
  description: string | null;
  assignee_id: string | null;
  state: TaskState;
  created_at: string;
  updated_at: string;
}

export interface Submission {
  id: string;
  task_id: string;
  submitted_by: string;
  content: string;
  created_at: string;
}

export interface Review {
  id: string;
  submission_id: string;
  reviewer_id: string;
  decision: "APPROVED" | "REJECTED";
  feedback: string | null;
  created_at: string;
}