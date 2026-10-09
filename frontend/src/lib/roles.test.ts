import { describe, expect, it } from "vitest";

import { can, canDeleteTask, canEditTask } from "./roles";

describe("роли интерфейса", () => {
  it("гость читает только публичное", () => {
    expect(can(null, "task:read_public")).toBe(true);
    expect(can(null, "task:create")).toBe(false);
  });

  it("пользователь не удаляет даже свою задачу", () => {
    expect(canDeleteTask("user", 5, 5)).toBe(false);
    expect(canEditTask("user", 5, null, 5)).toBe(true);
    expect(canEditTask("user", 7, null, 5)).toBe(false);
  });

  it("менеджер удаляет свою, администратор любую", () => {
    expect(canDeleteTask("manager", 3, 3)).toBe(true);
    expect(canDeleteTask("manager", 9, 3)).toBe(false);
    expect(canDeleteTask("admin", 9, 3)).toBe(true);
    expect(can("user", "user:manage_roles")).toBe(false);
    expect(can("admin", "user:manage_roles")).toBe(true);
  });
});
