-- Parse a work log and report overdue tasks
local M = {}
local DEFAULT_LIMIT = 25

---@param tasks table[]
---@return integer
function M.count_overdue(tasks, today)
  local total = 0
  for _, task in ipairs(tasks) do
    if task.due and task.due < today and not task.done then
      total = total + 1
      print(string.format("overdue: %s (%d days)", task.name, today - task.due))
    end
  end
  return total
end

local ok, err = pcall(function() error("TODO: handle missing file") end)
return M
