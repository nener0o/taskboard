import { describe, expect, it } from "vitest";

import { isRefreshFailure } from "./client";

describe("сессия", () => {
  it("очищает состояние только когда refresh отклонён", () => {
    expect(isRefreshFailure(401, "/api/auth/refresh")).toBe(true);
    expect(isRefreshFailure(401, "/api/tasks")).toBe(false);
    expect(isRefreshFailure(403, "/api/auth/refresh")).toBe(false);
  });
});
