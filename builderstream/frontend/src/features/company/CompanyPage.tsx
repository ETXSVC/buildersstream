import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, X, UserPlus, Users, Trash2 } from 'lucide-react';
import { fetchEmployees, createEmployee, updateEmployee } from '@/api/payroll';
import {
  fetchTeams,
  createTeam,
  deleteTeam,
  addTeamMember,
  removeTeamMember,
} from '@/api/teams';
import {
  EMPLOYMENT_TYPE_LABELS,
  EMPLOYMENT_TYPE_COLORS,
  TRADE_LABELS,
  type Employee,
  type EmploymentType,
  type EmployeeTrade,
} from '@/types/payroll';
import { KpiCard } from '@/components/KpiCard';
import {
  fetchMembers,
  inviteMember,
  updateMember,
  ROLE_LABELS,
  ROLE_COLORS,
  type Member,
  type MemberRole,
} from '@/api/members';

const ROLES: MemberRole[] = [
  'owner', 'admin', 'project_manager', 'estimator', 'accountant', 'field_worker', 'read_only',
];

function InviteMemberModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<MemberRole>('read_only');
  const [successMsg, setSuccessMsg] = useState('');

  const mutation = useMutation({
    mutationFn: () => inviteMember({ email, role }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['members'] });
      if ('detail' in data) {
        setSuccessMsg(data.detail);
      } else {
        onClose();
      }
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <form
        onClick={(e) => e.stopPropagation()}
        onSubmit={(e) => { e.preventDefault(); mutation.mutate(); }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4"
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Invite Team Member</h2>
          <button type="button" onClick={onClose}><X size={18} className="text-slate-400 hover:text-slate-600" /></button>
        </div>

        {successMsg ? (
          <div className="space-y-4">
            <p className="text-sm text-green-700 bg-green-50 rounded-lg p-3">{successMsg}</p>
            <div className="flex justify-end">
              <button type="button" onClick={onClose}
                className="px-4 py-2 rounded-lg text-sm bg-amber-500 text-white hover:bg-amber-600 font-medium">Close</button>
            </div>
          </div>
        ) : (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Email Address *</label>
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="colleague@example.com"
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Role *</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as MemberRole)}
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                ))}
              </select>
            </div>
            {mutation.isError && (
              <p className="text-xs text-red-500">Failed to invite. Please try again.</p>
            )}
            <div className="flex justify-end gap-2 pt-1">
              <button type="button" onClick={onClose}
                className="px-4 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100">Cancel</button>
              <button type="submit" disabled={mutation.isPending}
                className="px-4 py-2 rounded-lg text-sm bg-amber-500 text-white hover:bg-amber-600 disabled:opacity-50 font-medium">
                {mutation.isPending ? 'Inviting…' : 'Send Invite'}
              </button>
            </div>
          </>
        )}
      </form>
    </div>
  );
}

function EditMemberModal({ member, onClose }: { member: Member; onClose: () => void }) {
  const qc = useQueryClient();
  const [role, setRole] = useState<MemberRole>(member.role);
  const [isActive, setIsActive] = useState(member.is_active);

  const mutation = useMutation({
    mutationFn: () => updateMember(member.id, { role, is_active: isActive }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['members'] });
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <form
        onClick={(e) => e.stopPropagation()}
        onSubmit={(e) => { e.preventDefault(); mutation.mutate(); }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4"
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Edit Member</h2>
          <button type="button" onClick={onClose}><X size={18} className="text-slate-400 hover:text-slate-600" /></button>
        </div>

        <div>
          <p className="text-sm font-medium text-slate-900">{member.user_full_name || member.user_email}</p>
          <p className="text-xs text-slate-500">{member.user_email}</p>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as MemberRole)}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>{ROLE_LABELS[r]}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <input
            id="is_active"
            type="checkbox"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
            className="h-4 w-4 rounded border-slate-300 accent-amber-500"
          />
          <label htmlFor="is_active" className="text-sm text-slate-700">Active</label>
        </div>

        {mutation.isError && (
          <p className="text-xs text-red-500">Failed to save. Please try again.</p>
        )}
        <div className="flex justify-end gap-2 pt-1">
          <button type="button" onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100">Cancel</button>
          <button type="submit" disabled={mutation.isPending}
            className="px-4 py-2 rounded-lg text-sm bg-amber-500 text-white hover:bg-amber-600 disabled:opacity-50 font-medium">
            {mutation.isPending ? 'Saving…' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  );
}

function MembersTable({ members, onEdit }: { members: Member[]; onEdit: (m: Member) => void }) {
  if (members.length === 0) {
    return <p className="py-12 text-center text-sm text-slate-400">No team members yet.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 text-xs text-slate-500 uppercase tracking-wide">
            <th className="py-2 px-4 text-left">Name</th>
            <th className="py-2 px-4 text-left">Role</th>
            <th className="py-2 px-4 text-left">Status</th>
            <th className="py-2 px-4 text-left">Joined</th>
            <th className="py-2 px-4" />
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {members.map((m) => (
            <tr key={m.id} className="hover:bg-slate-50">
              <td className="py-2.5 px-4 font-medium text-slate-900">
                {m.user_full_name || '—'}
                <div className="text-xs text-slate-400 font-normal">{m.user_email}</div>
              </td>
              <td className="py-2.5 px-4">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_COLORS[m.role]}`}>
                  {ROLE_LABELS[m.role]}
                </span>
              </td>
              <td className="py-2.5 px-4">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${m.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                  {m.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="py-2.5 px-4 text-slate-500 text-xs">
                {m.accepted_at ? new Date(m.accepted_at).toLocaleDateString() : m.invited_at ? `Invited ${new Date(m.invited_at).toLocaleDateString()}` : '—'}
              </td>
              <td className="py-2.5 px-4">
                <button type="button" onClick={() => onEdit(m)} className="text-slate-400 hover:text-slate-700">
                  <Pencil size={14} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Teams Tab ──────────────────────────────────────────────────────────────────

function TeamsTab() {
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [addingTo, setAddingTo] = useState<string | null>(null);

  const { data: teams = [], isLoading } = useQuery({ queryKey: ['teams'], queryFn: fetchTeams });
  const { data: members = [] } = useQuery({ queryKey: ['members'], queryFn: fetchMembers });

  const createMut = useMutation({
    mutationFn: () => createTeam({ name: newName.trim(), description: newDesc.trim() }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['teams'] }); setShowCreate(false); setNewName(''); setNewDesc(''); },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteTeam(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['teams'] }); setExpanded(null); },
  });

  const addMut = useMutation({
    mutationFn: ({ teamId, userId }: { teamId: string; userId: string }) =>
      addTeamMember(teamId, userId),
    onSuccess: (_, { teamId }) => {
      qc.invalidateQueries({ queryKey: ['teams'] });
      qc.invalidateQueries({ queryKey: ['team', teamId] });
      setAddingTo(null);
    },
  });

  const removeMut = useMutation({
    mutationFn: ({ teamId, userId }: { teamId: string; userId: string }) =>
      removeTeamMember(teamId, userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['teams'] }),
  });

  const { data: teamDetail } = useQuery({
    queryKey: ['team', expanded],
    queryFn: () => fetchTeam(expanded!),
    enabled: !!expanded,
  });

  if (isLoading) {
    return <div className="flex h-40 items-center justify-center"><div className="h-6 w-6 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" /></div>;
  }

  const memberIdsInTeam = new Set((teamDetail?.members ?? []).map((m) => m.user));

  return (
    <div className="p-5 space-y-4">
      {/* Create form */}
      {showCreate ? (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3">
          <p className="text-sm font-medium text-slate-700">New Team</p>
          <input
            autoFocus
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Team name (e.g. Framing Crew)"
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
          <input
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
            placeholder="Description (optional)"
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
          {createMut.isError && <p className="text-xs text-red-500">Failed — name may already exist.</p>}
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={() => setShowCreate(false)} className="px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
            <button type="button" disabled={!newName.trim() || createMut.isPending} onClick={() => createMut.mutate()}
              className="px-3 py-1.5 text-sm bg-amber-500 text-white rounded-lg hover:bg-amber-600 disabled:opacity-50 font-medium">
              {createMut.isPending ? 'Creating…' : 'Create'}
            </button>
          </div>
        </div>
      ) : (
        <button type="button" onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 text-sm text-amber-600 hover:text-amber-700 font-medium">
          <Plus size={14} /> New Team
        </button>
      )}

      {teams.length === 0 && !showCreate && (
        <p className="py-8 text-center text-sm text-slate-400">No teams yet. Create one to get started.</p>
      )}

      {/* Team list */}
      <div className="space-y-2">
        {teams.map((team) => {
          const isExpanded = expanded === team.id;
          return (
            <div key={team.id} className="rounded-xl border border-slate-200 bg-white overflow-hidden">
              {/* Header */}
              <div
                role="button"
                tabIndex={0}
                onClick={() => setExpanded(isExpanded ? null : team.id)}
                onKeyDown={(e) => e.key === 'Enter' && setExpanded(isExpanded ? null : team.id)}
                className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-50"
              >
                <div className="flex items-center gap-3">
                  <Users size={16} className="text-amber-500 shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{team.name}</p>
                    {team.description && <p className="text-xs text-slate-400">{team.description}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500">{team.member_count} member{team.member_count !== 1 ? 's' : ''}</span>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); if (window.confirm(`Delete team "${team.name}"?`)) deleteMut.mutate(team.id); }}
                    className="text-slate-300 hover:text-red-500 p-1 rounded"
                    title="Delete team"
                  >
                    <Trash2 size={14} />
                  </button>
                  <svg className={`h-4 w-4 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* Expanded members */}
              {isExpanded && (
                <div className="border-t border-slate-100 px-4 py-3 space-y-2 bg-slate-50">
                  {(teamDetail?.members ?? []).length === 0 && (
                    <p className="text-xs text-slate-400 py-1">No members yet.</p>
                  )}
                  {(teamDetail?.members ?? []).map((m) => (
                    <div key={m.id} className="flex items-center justify-between rounded-lg bg-white px-3 py-2 text-sm border border-slate-100">
                      <div>
                        <span className="font-medium text-slate-800">{m.user_full_name || m.user_email}</span>
                        <span className={`ml-2 rounded-full px-2 py-0.5 text-xs font-medium ${m.role === 'lead' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'}`}>
                          {m.role === 'lead' ? 'Team Lead' : 'Member'}
                        </span>
                      </div>
                      <button type="button"
                        onClick={() => removeMut.mutate({ teamId: team.id, userId: m.user })}
                        className="text-slate-300 hover:text-red-500"><X size={14} /></button>
                    </div>
                  ))}

                  {/* Add member */}
                  {addingTo === team.id ? (
                    <div className="pt-1 space-y-2">
                      <select
                        defaultValue=""
                        onChange={(e) => { if (e.target.value) addMut.mutate({ teamId: team.id, userId: e.target.value }); }}
                        className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
                      >
                        <option value="">— Pick a member to add —</option>
                        {members.filter((m) => !memberIdsInTeam.has(m.user)).map((m) => (
                          <option key={m.id} value={m.user}>{m.user_full_name || m.user_email}</option>
                        ))}
                      </select>
                      <button type="button" onClick={() => setAddingTo(null)} className="text-xs text-slate-500 hover:underline">Cancel</button>
                    </div>
                  ) : (
                    <button type="button" onClick={() => setAddingTo(team.id)}
                      className="flex items-center gap-1 text-xs text-amber-600 hover:text-amber-700 font-medium pt-1">
                      <UserPlus size={12} /> Add member
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

const W2_TYPES: EmploymentType[] = ['w2_full_time', 'w2_part_time'];
const CONTRACTOR_TYPE: EmploymentType = '1099_contractor';

const TRADES = [
  'general','framing','electrical','plumbing','hvac','painting',
  'flooring','roofing','concrete','drywall','finish_carpentry','other',
] as EmployeeTrade[];

interface FormState {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  employment_type: EmploymentType;
  trade: EmployeeTrade;
  hire_date: string;
  base_hourly_rate: string;
}

const EMPTY_EMPLOYEE = (type: EmploymentType): FormState => ({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  employment_type: type,
  trade: 'general',
  hire_date: new Date().toISOString().slice(0, 10),
  base_hourly_rate: '',
});

function EmployeeModal({
  initial,
  defaultType,
  onClose,
}: {
  initial?: Employee;
  defaultType: EmploymentType;
  onClose: () => void;
}) {
  const qc = useQueryClient();
  const [form, setForm] = useState<FormState>(
    initial
      ? {
          first_name: initial.first_name,
          last_name: initial.last_name,
          email: initial.email,
          phone: initial.phone,
          employment_type: initial.employment_type,
          trade: initial.trade,
          hire_date: initial.hire_date,
          base_hourly_rate: initial.base_hourly_rate,
        }
      : EMPTY_EMPLOYEE(defaultType)
  );

  const mutation = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      initial ? updateEmployee(initial.id, data) : createEmployee(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['employees'] });
      onClose();
    },
  });

  const set = (k: keyof FormState, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({ ...form });
  };

  const title = initial
    ? `Edit ${initial.full_name}`
    : defaultType === CONTRACTOR_TYPE
    ? 'Add Contractor'
    : 'Add Employee';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <form
        onClick={(e) => e.stopPropagation()}
        onSubmit={submit}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-4 max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          <button type="button" onClick={onClose}><X size={18} className="text-slate-400 hover:text-slate-600" /></button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">First Name *</label>
            <input required value={form.first_name} onChange={(e) => set('first_name', e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Last Name *</label>
            <input required value={form.last_name} onChange={(e) => set('last_name', e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Email</label>
            <input type="email" value={form.email} onChange={(e) => set('email', e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Phone</label>
            <input value={form.phone} onChange={(e) => set('phone', e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Type *</label>
            <select value={form.employment_type} onChange={(e) => set('employment_type', e.target.value as EmploymentType)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400">
              {Object.entries(EMPLOYMENT_TYPE_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Trade *</label>
            <select value={form.trade} onChange={(e) => set('trade', e.target.value as EmployeeTrade)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400">
              {TRADES.map((t) => <option key={t} value={t}>{TRADE_LABELS[t]}</option>)}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Hire Date *</label>
            <input required type="date" value={form.hire_date} onChange={(e) => set('hire_date', e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Hourly Rate ($) *</label>
            <input required type="number" min="0" step="0.01" value={form.base_hourly_rate}
              onChange={(e) => set('base_hourly_rate', e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
          </div>
        </div>

        {mutation.isError && (
          <p className="text-xs text-red-500">Failed to save. Check all required fields.</p>
        )}

        <div className="flex justify-end gap-2 pt-1">
          <button type="button" onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100">Cancel</button>
          <button type="submit" disabled={mutation.isPending}
            className="px-4 py-2 rounded-lg text-sm bg-amber-500 text-white hover:bg-amber-600 disabled:opacity-50 font-medium">
            {mutation.isPending ? 'Saving…' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  );
}

function EmployeeTable({
  employees,
  onEdit,
}: {
  employees: Employee[];
  onEdit: (e: Employee) => void;
}) {
  if (employees.length === 0) {
    return <p className="py-12 text-center text-sm text-slate-400">No records yet.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 text-xs text-slate-500 uppercase tracking-wide">
            <th className="py-2 px-4 text-left">Name</th>
            <th className="py-2 px-4 text-left">Trade</th>
            <th className="py-2 px-4 text-left">Type</th>
            <th className="py-2 px-4 text-left">Rate / hr</th>
            <th className="py-2 px-4 text-left">Hire Date</th>
            <th className="py-2 px-4 text-left">Status</th>
            <th className="py-2 px-4" />
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {employees.map((emp) => (
            <tr key={emp.id} className="hover:bg-slate-50">
              <td className="py-2.5 px-4 font-medium text-slate-900">
                {emp.full_name}
                {emp.email && <div className="text-xs text-slate-400 font-normal">{emp.email}</div>}
              </td>
              <td className="py-2.5 px-4 text-slate-600">{TRADE_LABELS[emp.trade]}</td>
              <td className="py-2.5 px-4">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${EMPLOYMENT_TYPE_COLORS[emp.employment_type]}`}>
                  {EMPLOYMENT_TYPE_LABELS[emp.employment_type]}
                </span>
              </td>
              <td className="py-2.5 px-4 text-slate-600">${parseFloat(emp.base_hourly_rate).toFixed(2)}</td>
              <td className="py-2.5 px-4 text-slate-500">{emp.hire_date}</td>
              <td className="py-2.5 px-4">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${emp.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                  {emp.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="py-2.5 px-4">
                <button type="button" onClick={() => onEdit(emp)}
                  className="text-slate-400 hover:text-slate-700">
                  <Pencil size={14} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function CompanyPage() {
  const [tab, setTab] = useState<'employees' | 'contractors' | 'team-members' | 'teams'>('employees');
  const [modal, setModal] = useState<{ open: boolean; editing?: Employee }>({ open: false });
  const [inviteOpen, setInviteOpen] = useState(false);
  const [editingMember, setEditingMember] = useState<Member | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['employees'],
    queryFn: () => fetchEmployees({ page_size: '500' }),
  });

  const { data: membersData, isLoading: membersLoading } = useQuery({
    queryKey: ['members'],
    queryFn: fetchMembers,
  });

  const { data: teamsData } = useQuery({ queryKey: ['teams'], queryFn: fetchTeams });

  const all = data?.results ?? [];
  const employees = all.filter((e) => W2_TYPES.includes(e.employment_type));
  const contractors = all.filter((e) => e.employment_type === CONTRACTOR_TYPE);
  const activeEmp = employees.filter((e) => e.is_active).length;
  const activeCon = contractors.filter((e) => e.is_active).length;

  const members = membersData ?? [];
  const activeMembers = members.filter((m) => m.is_active).length;

  const defaultType: EmploymentType = tab === 'contractors' ? CONTRACTOR_TYPE : 'w2_full_time';
  const shown = tab === 'employees' ? employees : contractors;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Company</h1>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
        <KpiCard label="Total Employees" value={employees.length} icon="👷" accent="blue"
          sub={`${activeEmp} active`} onClick={() => setTab('employees')} />
        <KpiCard label="Total Contractors" value={contractors.length} icon="🔧" accent="amber"
          sub={`${activeCon} active`} onClick={() => setTab('contractors')} />
        <KpiCard label="Total Workforce" value={all.length} icon="🏗️" onClick={() => setTab('employees')} />
        <KpiCard label="Team Members" value={members.length} icon="🔑" accent="green"
          sub={`${activeMembers} active`} onClick={() => setTab('team-members')} />
        <KpiCard label="Teams" value={teamsData?.length ?? 0} icon="👥" accent="purple"
          onClick={() => setTab('teams')} />
      </div>

      {/* Tabs */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 pt-4 pb-0">
          <div className="flex gap-1 flex-wrap">
            {(['employees', 'contractors', 'team-members', 'teams'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                  tab === t
                    ? 'bg-white border border-b-white border-slate-200 text-amber-600 -mb-px'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {t === 'employees'
                  ? `Employees (${employees.length})`
                  : t === 'contractors'
                  ? `Contractors (${contractors.length})`
                  : t === 'team-members'
                  ? `Team Members (${members.length})`
                  : `Teams (${teamsData?.length ?? 0})`}
              </button>
            ))}
          </div>

          {tab === 'team-members' ? (
            <button
              type="button"
              onClick={() => setInviteOpen(true)}
              className="mb-2 flex items-center gap-1.5 rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-600"
            >
              <UserPlus size={14} />
              Invite Member
            </button>
          ) : tab === 'teams' ? null : (
            <button
              type="button"
              onClick={() => setModal({ open: true })}
              className="mb-2 flex items-center gap-1.5 rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-600"
            >
              <Plus size={14} />
              {tab === 'contractors' ? 'Add Contractor' : 'Add Employee'}
            </button>
          )}
        </div>

        {tab === 'teams' ? (
          <TeamsTab />
        ) : tab === 'team-members' ? (
          membersLoading ? (
            <div className="flex h-40 items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
            </div>
          ) : (
            <MembersTable members={members} onEdit={setEditingMember} />
          )
        ) : isLoading ? (
          <div className="flex h-40 items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
          </div>
        ) : (
          <EmployeeTable employees={shown} onEdit={(e) => setModal({ open: true, editing: e })} />
        )}
      </div>

      {modal.open && (
        <EmployeeModal
          initial={modal.editing}
          defaultType={defaultType}
          onClose={() => setModal({ open: false })}
        />
      )}
      {inviteOpen && <InviteMemberModal onClose={() => setInviteOpen(false)} />}
      {editingMember && <EditMemberModal member={editingMember} onClose={() => setEditingMember(null)} />}
    </div>
  );
}
