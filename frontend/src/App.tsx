import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { supabase } from "./lib/supabase";
import { api } from "./lib/api";
import type { Event, EventState, Review, Role, Submission, Task, TaskState, Team, TeamMember } from "./types";

type SessionUser = { id: string; email?: string | null };
type View = "overview" | "events" | "teams" | "tasks" | "reviews";

const EVENT_TRANSITIONS: Record<EventState, EventState[]> = {
  DRAFT: ["PLANNED"],
  PLANNED: ["ACTIVE", "CANCELLED"],
  ACTIVE: ["COMPLETED", "CANCELLED"],
  COMPLETED: [],
  CANCELLED: [],
};

const TASK_TRANSITIONS: Record<TaskState, TaskState[]> = {
  TODO: ["IN_PROGRESS"],
  IN_PROGRESS: ["SUBMITTED"],
  SUBMITTED: ["APPROVED", "REJECTED"],
  APPROVED: [],
  REJECTED: ["IN_PROGRESS"],
};

function App() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [role, setRole] = useState<Role | null>(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState("");
  const [view, setView] = useState<View>("overview");
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEventId, setSelectedEventId] = useState("");
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState("");
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [message, setMessage] = useState("");

  const selectedEvent = events.find((event) => event.id === selectedEventId) ?? null;
  const selectedTeam = teams.find((team) => team.id === selectedTeamId) ?? null;
  const selectedTask = tasks.find((task) => task.id === selectedTaskId) ?? null;

  const loadEvents = async () => {
    const data = await api.get<Event[]>("/events");
    setEvents(data);
    if (!selectedEventId && data[0]) setSelectedEventId(data[0].id);
  };

  const loadTeams = async (eventId: string) => {
    if (!eventId) return;
    const data = await api.get<Team[]>(`/events/${eventId}/teams`);
    setTeams(data);
    setSelectedTeamId((current) => data.some((team) => team.id === current) ? current : (data[0]?.id ?? ""));
  };

  const loadTasks = async (teamId: string) => {
    if (!teamId) {
      setTasks([]);
      return;
    }
    const data = await api.get<Task[]>(`/teams/${teamId}/tasks`);
    setTasks(data);
    setSelectedTaskId((current) => data.some((task) => task.id === current) ? current : (data[0]?.id ?? ""));
  };

  const loadSubmissions = async (taskId: string) => {
    if (!taskId) {
      setSubmissions([]);
      return;
    }
    const data = await api.get<Submission[]>(`/tasks/${taskId}/submissions`);
    setSubmissions(data);
  };

  const bootstrap = async () => {
    try {
      setLoading(true);
      const { data: sessionData } = await supabase.auth.getSession();
      if (!sessionData.session) return;
      setUser({ id: sessionData.session.user.id, email: sessionData.session.user.email });
      const identity = await api.get<{ user_id: string; role: Role }>("/events/me");
      setRole(identity.role);
      await loadEvents();
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Unable to load the application.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void bootstrap();
    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_OUT") {
        setUser(null);
        setRole(null);
        setEvents([]);
      } else if (session) {
        setUser({ id: session.user.id, email: session.user.email });
        void bootstrap();
      }
    });
    return () => data.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (selectedEventId) void loadTeams(selectedEventId);
  }, [selectedEventId]);

  useEffect(() => {
    if (selectedTeamId) void loadTasks(selectedTeamId);
  }, [selectedTeamId]);

  useEffect(() => {
    if (selectedTaskId) void loadSubmissions(selectedTaskId);
  }, [selectedTaskId]);

  const signOut = async () => {
    await supabase.auth.signOut();
  };

  if (loading) return <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">Loading FABRIC Ops…</div>;
  if (!user || !role) return <Login error={authError} />;

  return (
    <div className="app-shell min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-20 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-500/40 bg-cyan-500/10 text-sm font-bold text-cyan-300 shadow-[0_0_30px_rgba(34,211,238,0.25)]">F</div>
            <div>
              <div className="text-lg font-semibold tracking-tight text-white">FABRIC Ops</div>
              <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Event operations control plane</div>
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-cyan-300">{role}</span>
            <span className="hidden rounded-full border border-slate-700 bg-slate-900/80 px-2.5 py-1 text-slate-300 sm:inline">{user.email ?? user.id}</span>
            <button className="btn-secondary" onClick={signOut}>Sign out</button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[220px_1fr]">
        <aside className="panel h-fit p-2.5 lg:sticky lg:top-24">
          <div className="mb-2 px-2 pt-1 text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">Navigation</div>
          {(["overview", "events", "teams", "tasks", "reviews"] as View[]).map((item) => (
            <button
              key={item}
              onClick={() => setView(item)}
              className={`nav-button group ${view === item ? "active" : ""}`}
            >
              <span className="capitalize">{item}</span>
              <span className="h-1.5 w-1.5 rounded-full bg-slate-600 transition-colors duration-200 group-hover:bg-cyan-300" />
            </button>
          ))}
        </aside>

        <main className="space-y-6">
          {message && <div className="status-banner">{message}</div>}
          {view === "overview" && <Overview role={role} events={events} tasks={tasks} />}
          {view === "events" && (
            <EventsPanel
              role={role}
              events={events}
              selectedEvent={selectedEvent}
              onSelect={setSelectedEventId}
              onRefresh={loadEvents}
              onMessage={setMessage}
            />
          )}
          {view === "teams" && (
            <TeamsPanel
              role={role}
              event={selectedEvent}
              teams={teams}
              selectedTeam={selectedTeam}
              onSelect={setSelectedTeamId}
              onRefresh={() => { if (selectedEventId) return loadTeams(selectedEventId); }}
              onMessage={setMessage}
            />
          )}
          {view === "tasks" && (
            <TasksPanel
              role={role}
              event={selectedEvent}
              team={selectedTeam}
              tasks={tasks}
              selectedTask={selectedTask}
              userId={user.id}
              onSelect={setSelectedTaskId}
              onRefresh={() => { if (selectedTeamId) return loadTasks(selectedTeamId); }}
              onMessage={setMessage}
            />
          )}
          {view === "reviews" && (
            <ReviewsPanel
              role={role}
              task={selectedTask}
              submissions={submissions}
              onRefresh={() => { if (selectedTaskId) return loadSubmissions(selectedTaskId); }}
              onMessage={setMessage}
            />
          )}
        </main>
      </div>
    </div>
  );
}

function Login({ error }: { error: string }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState(error);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setLocalError("");
    const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });
    if (signInError) setLocalError(signInError.message);
    setBusy(false);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-10 sm:px-6">
      <form onSubmit={submit} className="panel w-full max-w-md space-y-6 overflow-hidden p-7 shadow-[0_0_0_1px_rgba(34,211,238,0.12),0_30px_80px_-40px_rgba(34,211,238,0.7)]">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-500/40 bg-cyan-500/10 text-sm font-bold text-cyan-300">F</div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-300">FABRIC Ops</p>
            <h1 className="mt-1 text-2xl font-semibold text-white">Sign in</h1>
          </div>
        </div>
        <p className="text-sm text-slate-400">Use your Supabase Auth account. Application role comes from the backend user record.</p>
        {localError && <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-300">{localError}</div>}
        <label className="block space-y-2 text-sm text-slate-300">Email<input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label className="block space-y-2 text-sm text-slate-300">Password<input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
    </div>
  );
}

function Overview({ role, events, tasks }: { role: Role; events: Event[]; tasks: Task[] }) {
  const active = events.filter((event) => event.state === "ACTIVE").length;
  const openTasks = tasks.filter((task) => !["APPROVED"].includes(task.state)).length;
  return (
    <>
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">Operations</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">Control plane</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">Role-aware access to the V1 event, team, task and review workflow.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Your role" value={role} />
        <Metric label="Active events" value={String(active)} />
        <Metric label="Visible open tasks" value={String(openTasks)} />
      </div>
      <div className="panel p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-white">Workflow</h2>
          <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-300">Live</span>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-2 text-sm text-slate-300">
          {["Event", "Team", "Task", "Submission", "Review", "Audit"].map((item, index) => (
            <span key={item} className="rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 shadow-[inset_0_1px_0_rgba(148,163,184,0.08)]">{index + 1}. {item}</span>
          ))}
        </div>
      </div>
    </>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <div className="text-[10px] uppercase tracking-[0.18em] text-slate-500">{label}</div>
      <div className="mt-3 text-3xl font-semibold tracking-tight text-white">{value}</div>
    </div>
  );
}

function EventsPanel({ role, events, selectedEvent, onSelect, onRefresh, onMessage }: {
  role: Role; events: Event[]; selectedEvent: Event | null; onSelect: (id: string) => void; onRefresh: () => Promise<void>; onMessage: (m: string) => void;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [busy, setBusy] = useState(false);
  const [dateError, setDateError] = useState("");

  const create = async (e: FormEvent) => {
    e.preventDefault();
    setDateError("");

    if (!startsAt || !endsAt) {
      setDateError("Start and end date/time are required.");
      return;
    }

    const start = new Date(startsAt);
    const end = new Date(endsAt);

    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      setDateError("Enter valid start and end date/time values.");
      return;
    }

    if (end <= start) {
      setDateError("End date/time must be after the start date/time.");
      return;
    }

    setBusy(true);
    try {
      await api.post<Event>("/events", {
        name,
        description: description || null,
        starts_at: start.toISOString(),
        ends_at: end.toISOString(),
      });
      setName(""); setDescription(""); setStartsAt(""); setEndsAt("");
      await onRefresh();
      onMessage("Event created.");
    } catch (error) { onMessage(error instanceof Error ? error.message : "Unable to create event."); }
    finally { setBusy(false); }
  };

  const transition = async (state: EventState) => {
    if (!selectedEvent) return;
    try {
      await api.patch<Event>(`/events/${selectedEvent.id}/state`, { state });
      await onRefresh();
      onMessage(`Event moved to ${state}.`);
    } catch (error) { onMessage(error instanceof Error ? error.message : "Unable to update event."); }
  };

  return (
    <section className="space-y-5">
      <PanelTitle title="Events" description="Select an event to drive the team and task views." />
      <div className="grid gap-5 lg:grid-cols-[1fr_360px]">
        <div className="panel overflow-hidden">
          <div className="divide-y divide-slate-800">
            {events.map((event) => (
              <button key={event.id} onClick={() => onSelect(event.id)} className={`block w-full px-5 py-4 text-left transition-all duration-200 ${selectedEvent?.id === event.id ? "bg-slate-800/80 shadow-[inset_0_0_0_1px_rgba(34,211,238,0.08)]" : "hover:bg-slate-900/80"}`}>
                <div className="flex items-center justify-between gap-3"><span className="font-medium text-white">{event.name}</span><StateBadge state={event.state} /></div>
                <p className="mt-2 text-xs text-slate-500">{new Date(event.starts_at).toLocaleString()} → {new Date(event.ends_at).toLocaleString()}</p>
              </button>
            ))}
            {!events.length && <div className="p-6 text-sm text-slate-500">No events visible for this account.</div>}
          </div>
        </div>

        {role === "ADMIN" && (
          <form onSubmit={create} className="panel space-y-4 p-5">
            <div className="mb-1 flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-white">Create event</h2>
              <span className="rounded-full border border-slate-700 bg-slate-950/80 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">Admin</span>
            </div>
            <input className="input" placeholder="Event name" value={name} onChange={(e) => setName(e.target.value)} required />
            <textarea className="input min-h-24" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
            <DateTimeField label="Start" value={startsAt} onChange={setStartsAt} />
            <DateTimeField label="End" value={endsAt} onChange={setEndsAt} min={startsAt} />
            {dateError && <p className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300">{dateError}</p>}
            <button className="btn-primary w-full" disabled={busy}>{busy ? "Creating…" : "Create event"}</button>
          </form>
        )}
      </div>
      {selectedEvent && <div className="panel p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div><h2 className="text-lg font-semibold text-white">{selectedEvent.name}</h2><p className="mt-1 text-sm text-slate-400">{selectedEvent.description || "No description."}</p></div>
          <div className="flex flex-wrap gap-2">
            {EVENT_TRANSITIONS[selectedEvent.state].map((next) => (
              <button key={next} className={next === "CANCELLED" ? "btn-danger" : "btn-secondary"} onClick={() => transition(next)} disabled={role === "MEMBER"}>{next}</button>
            ))}
          </div>
        </div>
      </div>}
    </section>
  );
}

function DateTimeField({
  label,
  value,
  onChange,
  min,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  min?: string;
}) {
  const [date, time] = value.split("T");
  const minDate = min?.split("T")[0];
  const minTime = min?.split("T")[1];

  const updateDate = (nextDate: string) => {
    onChange(nextDate && time ? nextDate + "T" + time : nextDate);
  };

  const updateTime = (nextTime: string) => {
    onChange(date && nextTime ? date + "T" + nextTime : nextTime);
  };

  return (
    <div className="space-y-2">
      <span className="block text-sm font-medium text-slate-300">{label}</span>
      <div className="grid grid-cols-[1fr_0.8fr] gap-2">
        <label className="field-shell">
          <span className="sr-only">{label} date</span>
          <input
            className="input w-full"
            type="date"
            value={date ?? ""}
            min={minDate}
            onChange={(e) => updateDate(e.target.value)}
            required
          />
        </label>
        <label className="field-shell">
          <span className="sr-only">{label} time</span>
          <input
            className="input w-full"
            type="time"
            value={time ?? ""}
            min={minDate === date ? minTime : undefined}
            step={300}
            onChange={(e) => updateTime(e.target.value)}
            required
          />
        </label>
      </div>
    </div>
  );
}

function TeamsPanel({ role, event, teams, selectedTeam, onSelect, onRefresh, onMessage }: {
  role: Role; event: Event | null; teams: Team[]; selectedTeam: Team | null; onSelect: (id: string) => void; onRefresh: () => Promise<void> | void; onMessage: (m: string) => void;
}) {
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [memberId, setMemberId] = useState("");
  const [memberRole, setMemberRole] = useState<"LEAD" | "MEMBER">("MEMBER");
  const [members, setMembers] = useState<TeamMember[]>([]);

  const loadMembers = async (teamId: string) => setMembers(await api.get<TeamMember[]>(`/teams/${teamId}/members`));
  useEffect(() => { if (selectedTeam) void loadMembers(selectedTeam.id); else setMembers([]); }, [selectedTeam?.id]);

  const create = async (e: FormEvent) => {
    e.preventDefault();
    if (!event) return;
    setBusy(true);
    try {
      await api.post<Team>(`/events/${event.id}/teams`, { name });
      setName(""); await onRefresh(); onMessage("Team created.");
    } catch (error) { onMessage(error instanceof Error ? error.message : "Unable to create team."); }
    finally { setBusy(false); }
  };

  const addMember = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedTeam) return;
    try {
      await api.post<TeamMember>(`/teams/${selectedTeam.id}/members`, { user_id: memberId, membership_role: memberRole });
      setMemberId(""); await loadMembers(selectedTeam.id); onMessage("Member added.");
    } catch (error) { onMessage(error instanceof Error ? error.message : "Unable to add member."); }
  };

  const removeMember = async (id: string) => {
    if (!selectedTeam) return;
    try { await api.delete(`/teams/${selectedTeam.id}/members/${id}`); await loadMembers(selectedTeam.id); onMessage("Member removed."); }
    catch (error) { onMessage(error instanceof Error ? error.message : "Unable to remove member."); }
  };

  return (
    <section className="space-y-5">
      <PanelTitle title="Teams" description={event ? `Teams for ${event.name}` : "Select an event first."} />
      {!event ? <EmptyState text="Select an event from the Events view." /> : (
        <div className="grid gap-5 lg:grid-cols-[1fr_380px]">
          <div className="panel overflow-hidden">
            <div className="divide-y divide-slate-800">
              {teams.map((team) => <button key={team.id} onClick={() => onSelect(team.id)} className={`block w-full px-5 py-4 text-left transition-all duration-200 ${selectedTeam?.id === team.id ? "bg-slate-800/80 shadow-[inset_0_0_0_1px_rgba(34,211,238,0.08)]" : "hover:bg-slate-900/80"}`}><div className="font-medium text-white">{team.name}</div><div className="mt-1 text-xs text-slate-500">{team.id}</div></button>)}
              {!teams.length && <div className="p-6 text-sm text-slate-500">No teams visible for this event.</div>}
            </div>
          </div>
          <div className="space-y-5">
            {role === "ADMIN" && <form onSubmit={create} className="panel space-y-3 p-5"><h2 className="text-lg font-semibold text-white">Create team</h2><input className="input" placeholder="Team name" value={name} onChange={(e) => setName(e.target.value)} required /><button className="btn-primary w-full" disabled={busy}>{busy ? "Creating…" : "Create team"}</button></form>}
            {selectedTeam && <div className="panel p-5"><div className="flex items-center justify-between"><h2 className="font-semibold text-white">{selectedTeam.name}</h2><span className="text-xs text-slate-500">{members.length} members</span></div><div className="mt-4 space-y-2">{members.map((member) => <div key={member.user_id} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/80 p-3 text-xs"><div><div className="text-slate-200">{member.user_id}</div><div className="text-slate-500">{member.membership_role}</div></div>{role !== "MEMBER" && <button className="text-rose-400 hover:text-rose-300" onClick={() => removeMember(member.user_id)}>Remove</button>}</div>)}</div>{role !== "MEMBER" && <form onSubmit={addMember} className="mt-4 space-y-2 border-t border-slate-800 pt-4"><input className="input" placeholder="User UUID" value={memberId} onChange={(e) => setMemberId(e.target.value)} required /><div className="flex gap-2"><select className="input" value={memberRole} onChange={(e) => setMemberRole(e.target.value as "LEAD" | "MEMBER")}><option value="MEMBER">MEMBER</option><option value="LEAD">LEAD</option></select><button className="btn-primary">Add</button></div></form>}</div>}
          </div>
        </div>
      )}
    </section>
  );
}

function TasksPanel({ role, event, team, tasks, selectedTask, userId, onSelect, onRefresh, onMessage }: {
  role: Role; event: Event | null; team: Team | null; tasks: Task[]; selectedTask: Task | null; userId: string; onSelect: (id: string) => void; onRefresh: () => Promise<void> | void; onMessage: (m: string) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [submission, setSubmission] = useState("");
  const canCreate = role === "ADMIN" || role === "LEAD";

  const create = async (e: FormEvent) => {
    e.preventDefault();
    if (!event || !team) return;
    try {
      await api.post<Task>(`/events/${event.id}/teams/${team.id}/tasks`, { title, description: description || null, assignee_id: assigneeId });
      setTitle(""); setDescription(""); setAssigneeId(""); await onRefresh(); onMessage("Task created.");
    } catch (error) { onMessage(error instanceof Error ? error.message : "Unable to create task."); }
  };

  const transition = async (state: TaskState) => {
    if (!selectedTask) return;
    try { await api.patch<Task>(`/tasks/${selectedTask.id}/state`, { state }); await onRefresh(); onMessage(`Task moved to ${state}.`); }
    catch (error) { onMessage(error instanceof Error ? error.message : "Unable to update task."); }
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedTask) return;
    try { await api.post<Submission>(`/tasks/${selectedTask.id}/submissions`, { content: submission }); setSubmission(""); await onRefresh(); onMessage("Submission created."); }
    catch (error) { onMessage(error instanceof Error ? error.message : "Unable to submit task."); }
  };

  const allowed = TASK_TRANSITIONS[selectedTask?.state ?? "TODO"].filter((next) => {
    if (role === "ADMIN") return next === "IN_PROGRESS";
    if (role === "LEAD") return false;
    return next === "IN_PROGRESS" && selectedTask?.assignee_id === userId;
  });

  return (
    <section className="space-y-5">
      <PanelTitle title="Tasks" description={team ? `Tasks for ${team.name}` : "Select a team first."} />
      {!team ? <EmptyState text="Select a team from the Teams view." /> : (
        <div className="grid gap-5 lg:grid-cols-[1fr_430px]">
          <div className="panel overflow-hidden">
            <div className="divide-y divide-slate-800">
              {tasks.map((task) => <button key={task.id} onClick={() => onSelect(task.id)} className={`block w-full px-5 py-4 text-left transition-all duration-200 ${selectedTask?.id === task.id ? "bg-slate-800/80 shadow-[inset_0_0_0_1px_rgba(34,211,238,0.08)]" : "hover:bg-slate-900/80"}`}><div className="flex items-center justify-between gap-3"><span className="font-medium text-white">{task.title}</span><StateBadge state={task.state} /></div><div className="mt-1 text-xs text-slate-500">Assignee: {task.assignee_id ?? "unassigned"}</div></button>)}
              {!tasks.length && <div className="p-6 text-sm text-slate-500">No tasks visible for this team.</div>}
            </div>
          </div>
          <div className="space-y-5">
            {canCreate && <form onSubmit={create} className="panel space-y-3 p-5"><h2 className="text-lg font-semibold text-white">Create task</h2><input className="input" placeholder="Task title" value={title} onChange={(e) => setTitle(e.target.value)} required /><textarea className="input min-h-24" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} /><input className="input" placeholder="Assignee user UUID" value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)} required /><button className="btn-primary w-full">Create task</button></form>}
            {selectedTask && <div className="panel space-y-4 p-5"><div><h2 className="text-lg font-semibold text-white">{selectedTask.title}</h2><p className="mt-2 text-sm text-slate-400">{selectedTask.description || "No description."}</p></div><div className="flex flex-wrap gap-2">{allowed.map((next) => <button key={next} className="btn-secondary" onClick={() => transition(next)}>{next}</button>)}</div>{role === "MEMBER" && selectedTask.assignee_id === userId && selectedTask.state === "IN_PROGRESS" && <form onSubmit={submit} className="space-y-2 border-t border-slate-800 pt-4"><textarea className="input min-h-28" placeholder="Submission content or reference" value={submission} onChange={(e) => setSubmission(e.target.value)} required /><button className="btn-primary w-full">Submit work</button></form>}</div>}
          </div>
        </div>
      )}
    </section>
  );
}

function ReviewsPanel({ role, task, submissions, onRefresh, onMessage }: {
  role: Role; task: Task | null; submissions: Submission[]; onRefresh: () => Promise<void> | void; onMessage: (m: string) => void;
}) {
  const [feedback, setFeedback] = useState("");
  if (!task) return <section className="space-y-5"><PanelTitle title="Reviews" description="Review submissions for the selected task." /><EmptyState text="Select a task from the Tasks view." /></section>;

  const review = async (submissionId: string, decision: "APPROVED" | "REJECTED") => {
    try { await api.post<Review>(`/submissions/${submissionId}/reviews`, { decision, feedback: feedback || null }); setFeedback(""); await onRefresh(); onMessage(`Submission ${decision.toLowerCase()}.`); }
    catch (error) { onMessage(error instanceof Error ? error.message : "Unable to review submission."); }
  };

  return (
    <section className="space-y-5">
      <PanelTitle title="Reviews" description={`${task.title} · ${task.state}`} />
      {submissions.map((submission) => <div key={submission.id} className="panel p-5"><div className="flex items-center justify-between"><span className="text-xs text-slate-500">{submission.id}</span><span className="text-xs text-slate-500">{new Date(submission.created_at).toLocaleString()}</span></div><p className="mt-4 whitespace-pre-wrap text-sm text-slate-200">{submission.content}</p>{role !== "MEMBER" && task.state === "SUBMITTED" && <div className="mt-4 space-y-3 border-t border-slate-800 pt-4"><textarea className="input min-h-20" placeholder="Review feedback" value={feedback} onChange={(e) => setFeedback(e.target.value)} /><div className="flex gap-2"><button className="btn-primary" onClick={() => review(submission.id, "APPROVED")}>Approve</button><button className="btn-danger" onClick={() => review(submission.id, "REJECTED")}>Reject</button></div></div>}</div>)}
      {!submissions.length && <EmptyState text="No submissions yet." />}
    </section>
  );
}

function PanelTitle({ title, description }: { title: string; description: string }) {
  return <div><h1 className="text-2xl font-semibold tracking-tight text-white">{title}</h1><p className="mt-2 text-sm text-slate-400">{description}</p></div>;
}

function EmptyState({ text }: { text: string }) {
  return <div className="panel p-8 text-sm text-slate-500">{text}</div>;
}

function StateBadge({ state }: { state: string }) {
  return <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-cyan-300">{state}</span>;
}

export default App;