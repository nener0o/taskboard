const MATRIX: Record<string, string[]> = {
  user: ["task:read_public", "task:read_own", "task:create", "task:update_own", "file:upload", "file:delete_own"],
  manager: [
    "task:read_public",
    "task:read_own",
    "task:read_all",
    "task:create",
    "task:update_own",
    "task:update_any",
    "task:delete_own",
    "task:moderate",
    "file:upload",
    "file:delete_own",
    "file:delete_any",
    "user:read",
  ],
  admin: [
    "task:read_public",
    "task:read_own",
    "task:read_all",
    "task:create",
    "task:update_own",
    "task:update_any",
    "task:delete_own",
    "task:delete_any",
    "task:moderate",
    "file:upload",
    "file:delete_own",
    "file:delete_any",
    "user:read",
    "user:manage_roles",
  ],
};

export function can(role: string | null | undefined, permission: string): boolean {
  if (!role) return permission === "task:read_public";
  return MATRIX[role]?.includes(permission) ?? false;
}

export function canDeleteTask(role: string, ownerId: number, userId: number): boolean {
  if (can(role, "task:delete_any")) return true;
  return ownerId === userId && can(role, "task:delete_own");
}

export function canEditTask(role: string, ownerId: number, assigneeId: number | null, userId: number): boolean {
  if (can(role, "task:update_any")) return true;
  const owns = ownerId === userId || assigneeId === userId;
  return owns && can(role, "task:update_own");
}
