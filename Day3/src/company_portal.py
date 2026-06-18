"""
회사 홈페이지.
할일 목록을 관리한다.
할일을 추가 수정 삭제할 수 있는 기능을 제공한다.
개발은 FastAPI 기반으로 한다.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="회사 포털 - 할일 관리")

# 인메모리 저장소
todos: dict[int, dict] = {}
next_id = 1


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    done: bool = False


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None


# 할일 목록 조회
@app.get("/todos")
def get_todos():
    return list(todos.values())


# 할일 단건 조회
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없습니다.")
    return todos[todo_id]


# 할일 추가
@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    global next_id
    item = {"id": next_id, **todo.dict()}
    todos[next_id] = item
    next_id += 1
    return item


# 할일 수정
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없습니다.")
    updated = todos[todo_id].copy()
    for field, value in todo.dict(exclude_unset=True).items():
        updated[field] = value
    todos[todo_id] = updated
    return updated


# 할일 삭제
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없습니다.")
    del todos[todo_id]


# Web UI
@app.get("/", response_class=HTMLResponse)
def ui():
    return r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>할일 관리 포털</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Space+Grotesk:wght@400;600;700&display=swap');

  :root {
    --bg-1: #f7f9ee;
    --bg-2: #e8f4f8;
    --card: #ffffff;
    --ink: #20333b;
    --muted: #5f727b;
    --line: #d4e0e5;
    --brand: #0e8a72;
    --brand-strong: #0a6a56;
    --danger: #cb3f3f;
    --warn: #e79a2d;
    --radius: 14px;
    --shadow: 0 10px 28px rgba(22, 52, 64, 0.12);
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    min-height: 100vh;
    color: var(--ink);
    background:
      radial-gradient(circle at 10% 10%, #cfeee5 0%, transparent 28%),
      radial-gradient(circle at 86% 16%, #d2edf7 0%, transparent 24%),
      linear-gradient(165deg, var(--bg-1), var(--bg-2));
    font-family: 'Gowun Dodum', sans-serif;
    padding: 30px 14px 50px;
  }

  .shell {
    max-width: 880px;
    margin: 0 auto;
    display: grid;
    gap: 14px;
  }

  .hero {
    background: linear-gradient(120deg, #14323b, #286473);
    color: #f7fcff;
    border-radius: 18px;
    padding: 22px;
    box-shadow: var(--shadow);
  }

  .hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    margin: 0;
    font-size: clamp(1.5rem, 3vw, 2rem);
    letter-spacing: 0.02em;
  }

  .hero p {
    margin: 8px 0 0;
    color: #d6edf4;
    font-size: 0.96rem;
  }

  .panel {
    background: var(--card);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid rgba(255, 255, 255, 0.7);
    padding: 16px;
  }

  .panel-title {
    margin: 0 0 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.02rem;
  }

  .form-grid {
    display: grid;
    gap: 8px;
    grid-template-columns: 1fr;
  }

  .input,
  .textarea,
  .search {
    width: 100%;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: #fff;
    padding: 11px 12px;
    font-size: 0.96rem;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  .input:focus,
  .textarea:focus,
  .search:focus {
    border-color: #38a28e;
    box-shadow: 0 0 0 3px rgba(56, 162, 142, 0.15);
  }

  .textarea {
    min-height: 76px;
    resize: vertical;
  }

  .actions-row {
    margin-top: 2px;
    display: flex;
    justify-content: flex-end;
  }

  .btn {
    border: 0;
    border-radius: 10px;
    padding: 9px 14px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.87rem;
    cursor: pointer;
    transition: transform 0.16s ease, opacity 0.16s ease, background-color 0.16s ease;
  }

  .btn:active { transform: scale(0.98); }

  .btn-primary { background: var(--brand); color: #fff; }
  .btn-primary:hover { background: var(--brand-strong); }
  .btn-secondary { background: #dbeff3; color: #1f404b; }
  .btn-secondary:hover { background: #cce4ea; }
  .btn-danger { background: #fce8e8; color: #9a2a2a; }
  .btn-danger:hover { background: #f8d7d7; }
  .btn-warning { background: #fff2df; color: #8a5606; }
  .btn-warning:hover { background: #fde8cb; }
  .btn[disabled] { cursor: not-allowed; opacity: 0.55; }

  .toolbar {
    display: grid;
    gap: 10px;
    grid-template-columns: 1fr;
  }

  .stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .chip {
    border-radius: 999px;
    font-size: 0.8rem;
    padding: 7px 10px;
    border: 1px solid #d4e5eb;
    color: #294b56;
    background: #f4fafc;
  }

  .filters {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  .filter-btn {
    border: 1px solid #c8dde4;
    padding: 7px 11px;
    border-radius: 999px;
    background: #fff;
    color: #365760;
    font-size: 0.82rem;
    cursor: pointer;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
  }

  .filter-btn.active {
    background: #174e5c;
    color: #fff;
    border-color: #174e5c;
  }

  .todo-list {
    list-style: none;
    margin: 10px 0 0;
    padding: 0;
    display: grid;
    gap: 8px;
  }

  .todo-item {
    display: grid;
    gap: 8px;
    grid-template-columns: auto 1fr auto;
    align-items: start;
    border: 1px solid #dbe7ec;
    border-radius: 12px;
    padding: 12px;
    background: #fff;
    animation: fade-in 0.25s ease;
  }

  .todo-item.done {
    background: #f8fbf9;
    border-color: #dce9e2;
  }

  .todo-item.done .todo-title {
    text-decoration: line-through;
    color: #6e838b;
  }

  .todo-main {
    min-width: 0;
  }

  .todo-title {
    font-weight: 700;
    font-size: 1rem;
    line-height: 1.35;
    word-break: break-word;
  }

  .todo-desc {
    margin-top: 3px;
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.4;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .todo-meta {
    margin-top: 6px;
    font-size: 0.77rem;
    color: #7b8e96;
  }

  .todo-actions {
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .todo-checkbox {
    width: 18px;
    height: 18px;
    margin-top: 4px;
    cursor: pointer;
    accent-color: #177663;
  }

  .empty {
    text-align: center;
    padding: 16px;
    color: #6e838b;
    background: #f8fbfd;
    border-radius: 10px;
    border: 1px dashed #cadde4;
  }

  .loading {
    text-align: center;
    color: #57717b;
    font-size: 0.9rem;
    padding: 12px;
  }

  .toast {
    position: fixed;
    right: 18px;
    bottom: 20px;
    background: #1f3d47;
    color: #fff;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.86rem;
    opacity: 0;
    transform: translateY(8px);
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.2s ease;
    z-index: 999;
  }

  .toast.show {
    opacity: 1;
    transform: translateY(0);
  }

  .toast.error { background: #7f1f1f; }
  .toast.success { background: #115845; }

  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(16, 35, 40, 0.45);
    align-items: center;
    justify-content: center;
    z-index: 800;
    padding: 16px;
  }

  .modal-overlay.show { display: flex; }

  .modal {
    width: 100%;
    max-width: 460px;
    background: #fff;
    border-radius: 14px;
    border: 1px solid #dde8ec;
    padding: 16px;
    box-shadow: var(--shadow);
  }

  .modal h2 {
    margin: 0 0 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.04rem;
  }

  .modal-actions {
    margin-top: 10px;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  @keyframes fade-in {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (min-width: 760px) {
    .form-grid {
      grid-template-columns: 1.2fr 1fr;
      grid-template-areas:
        'title desc'
        'actions actions';
    }
    #new-title { grid-area: title; }
    #new-desc { grid-area: desc; min-height: 48px; }
    .actions-row { grid-area: actions; }

    .toolbar {
      grid-template-columns: 1.3fr auto;
      align-items: center;
    }
  }
</style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>Team Planner</h1>
      <p>작업을 빠르게 추가하고, 우선순위처럼 관리하듯 완료 상태를 깔끔하게 추적하세요.</p>
    </section>

    <section class="panel">
      <h2 class="panel-title">새 할일 추가</h2>
      <div class="form-grid">
        <input id="new-title" class="input" type="text" placeholder="제목 입력 (필수)" maxlength="120" />
        <textarea id="new-desc" class="textarea" placeholder="설명 입력 (선택)"></textarea>
        <div class="actions-row">
          <button id="add-btn" class="btn btn-primary" type="button">추가</button>
        </div>
      </div>
    </section>

    <section class="panel">
      <h2 class="panel-title">할일 목록</h2>

      <div class="toolbar">
        <input id="search" class="search" type="text" placeholder="제목/설명 검색" />
        <button id="clear-completed" class="btn btn-secondary" type="button">완료 항목 정리</button>
      </div>

      <div class="stats" style="margin-top:10px;">
        <span class="chip" id="stat-all">전체 0개</span>
        <span class="chip" id="stat-open">진행중 0개</span>
        <span class="chip" id="stat-done">완료 0개</span>
      </div>

      <div class="filters" style="margin-top:10px;">
        <button class="filter-btn active" data-filter="all" type="button">전체</button>
        <button class="filter-btn" data-filter="open" type="button">진행중</button>
        <button class="filter-btn" data-filter="done" type="button">완료</button>
      </div>

      <ul id="todo-list" class="todo-list" aria-live="polite">
        <li class="loading">불러오는 중...</li>
      </ul>
    </section>
  </main>

  <div id="toast" class="toast" role="status" aria-live="polite"></div>

  <div id="modal-overlay" class="modal-overlay" aria-hidden="true">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <h2 id="modal-title">할일 수정</h2>
      <input id="edit-title" class="input" type="text" placeholder="제목" maxlength="120" />
      <textarea id="edit-desc" class="textarea" placeholder="설명"></textarea>
      <div class="modal-actions">
        <button id="cancel-edit" class="btn btn-secondary" type="button">취소</button>
        <button id="save-edit" class="btn btn-primary" type="button">저장</button>
      </div>
    </div>
  </div>

<script>
const els = {
  list: document.getElementById('todo-list'),
  addBtn: document.getElementById('add-btn'),
  title: document.getElementById('new-title'),
  desc: document.getElementById('new-desc'),
  search: document.getElementById('search'),
  filters: [...document.querySelectorAll('.filter-btn')],
  clearCompleted: document.getElementById('clear-completed'),
  statAll: document.getElementById('stat-all'),
  statOpen: document.getElementById('stat-open'),
  statDone: document.getElementById('stat-done'),
  modalOverlay: document.getElementById('modal-overlay'),
  editTitle: document.getElementById('edit-title'),
  editDesc: document.getElementById('edit-desc'),
  cancelEdit: document.getElementById('cancel-edit'),
  saveEdit: document.getElementById('save-edit'),
  toast: document.getElementById('toast')
};

let todos = [];
let currentFilter = 'all';
let searchText = '';
let editingId = null;
let toastTimer = null;

function showToast(message, type = 'success') {
  clearTimeout(toastTimer);
  els.toast.textContent = message;
  els.toast.className = `toast ${type} show`;
  toastTimer = setTimeout(() => {
    els.toast.className = 'toast';
  }, 1900);
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function setLoading(loading) {
  els.addBtn.disabled = loading;
  els.saveEdit.disabled = loading;
  els.clearCompleted.disabled = loading;
}

async function request(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    let msg = '요청 중 오류가 발생했습니다.';
    try {
      const data = await res.json();
      msg = data.detail || msg;
    } catch (e) {
      // 응답이 JSON이 아닐 수 있으므로 기본 메시지를 사용한다.
    }
    throw new Error(msg);
  }
  if (res.status === 204) {
    return null;
  }
  return res.json();
}

function getFilteredTodos() {
  return todos.filter((todo) => {
    if (currentFilter === 'open' && todo.done) {
      return false;
    }
    if (currentFilter === 'done' && !todo.done) {
      return false;
    }
    if (!searchText) {
      return true;
    }
    const haystack = `${todo.title || ''} ${todo.description || ''}`.toLowerCase();
    return haystack.includes(searchText.toLowerCase());
  });
}

function updateStats() {
  const total = todos.length;
  const doneCount = todos.filter((t) => t.done).length;
  const openCount = total - doneCount;
  els.statAll.textContent = `전체 ${total}개`;
  els.statOpen.textContent = `진행중 ${openCount}개`;
  els.statDone.textContent = `완료 ${doneCount}개`;
}

function renderTodos() {
  updateStats();
  const items = getFilteredTodos();

  if (items.length === 0) {
    const text = todos.length === 0
      ? '할일이 없습니다. 첫 작업을 추가해보세요.'
      : '필터 조건에 맞는 항목이 없습니다.';
    els.list.innerHTML = `<li class="empty">${text}</li>`;
    return;
  }

  els.list.innerHTML = items.map((todo) => {
    const doneClass = todo.done ? 'done' : '';
    const description = todo.description
      ? `<div class="todo-desc">${escapeHtml(todo.description)}</div>`
      : '';

    return `
      <li class="todo-item ${doneClass}">
        <input class="todo-checkbox" type="checkbox" data-action="toggle" data-id="${todo.id}" ${todo.done ? 'checked' : ''} />
        <div class="todo-main">
          <div class="todo-title">${escapeHtml(todo.title)}</div>
          ${description}
          <div class="todo-meta">ID: ${todo.id}</div>
        </div>
        <div class="todo-actions">
          <button class="btn btn-warning" data-action="edit" data-id="${todo.id}" type="button">수정</button>
          <button class="btn btn-danger" data-action="delete" data-id="${todo.id}" type="button">삭제</button>
        </div>
      </li>
    `;
  }).join('');
}

async function loadTodos() {
  setLoading(true);
  els.list.innerHTML = '<li class="loading">불러오는 중...</li>';
  try {
    todos = await request('/todos');
    renderTodos();
  } catch (error) {
    els.list.innerHTML = `<li class="empty">${escapeHtml(error.message)}</li>`;
    showToast(error.message, 'error');
  } finally {
    setLoading(false);
  }
}

async function addTodo() {
  const title = els.title.value.trim();
  if (!title) {
    showToast('제목을 입력하세요.', 'error');
    els.title.focus();
    return;
  }

  const description = els.desc.value.trim();
  setLoading(true);
  try {
    await request('/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description: description || null })
    });
    els.title.value = '';
    els.desc.value = '';
    await loadTodos();
    showToast('할일이 추가되었습니다.');
    els.title.focus();
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setLoading(false);
  }
}

async function removeTodo(id) {
  const ok = window.confirm('이 항목을 삭제할까요?');
  if (!ok) {
    return;
  }
  setLoading(true);
  try {
    await request(`/todos/${id}`, { method: 'DELETE' });
    await loadTodos();
    showToast('삭제되었습니다.');
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setLoading(false);
  }
}

async function toggleTodo(id, done) {
  setLoading(true);
  try {
    await request(`/todos/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ done })
    });
    const todo = todos.find((item) => item.id === id);
    if (todo) {
      todo.done = done;
    }
    renderTodos();
  } catch (error) {
    showToast(error.message, 'error');
    await loadTodos();
  } finally {
    setLoading(false);
  }
}

function openEdit(id) {
  const todo = todos.find((item) => item.id === id);
  if (!todo) {
    showToast('대상 항목을 찾지 못했습니다.', 'error');
    return;
  }
  editingId = id;
  els.editTitle.value = todo.title || '';
  els.editDesc.value = todo.description || '';
  els.modalOverlay.classList.add('show');
  els.modalOverlay.setAttribute('aria-hidden', 'false');
  els.editTitle.focus();
}

function closeEdit() {
  editingId = null;
  els.modalOverlay.classList.remove('show');
  els.modalOverlay.setAttribute('aria-hidden', 'true');
}

async function saveEdit() {
  if (editingId === null) {
    return;
  }
  const title = els.editTitle.value.trim();
  if (!title) {
    showToast('제목을 입력하세요.', 'error');
    els.editTitle.focus();
    return;
  }
  const description = els.editDesc.value.trim();
  setLoading(true);
  try {
    await request(`/todos/${editingId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description: description || null })
    });
    closeEdit();
    await loadTodos();
    showToast('수정이 완료되었습니다.');
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setLoading(false);
  }
}

async function clearCompleted() {
  const completed = todos.filter((todo) => todo.done);
  if (completed.length === 0) {
    showToast('완료된 항목이 없습니다.', 'error');
    return;
  }
  setLoading(true);
  try {
    await Promise.all(completed.map((todo) => request(`/todos/${todo.id}`, { method: 'DELETE' })));
    await loadTodos();
    showToast('완료 항목이 정리되었습니다.');
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setLoading(false);
  }
}

els.addBtn.addEventListener('click', addTodo);
els.title.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    addTodo();
  }
});
els.search.addEventListener('input', (event) => {
  searchText = event.target.value.trim();
  renderTodos();
});
els.filters.forEach((btn) => {
  btn.addEventListener('click', () => {
    currentFilter = btn.dataset.filter;
    els.filters.forEach((node) => node.classList.toggle('active', node === btn));
    renderTodos();
  });
});
els.clearCompleted.addEventListener('click', clearCompleted);

els.list.addEventListener('click', (event) => {
  const target = event.target.closest('[data-action]');
  if (!target) {
    return;
  }
  const id = Number(target.dataset.id);
  const action = target.dataset.action;
  if (action === 'delete') {
    removeTodo(id);
  }
  if (action === 'edit') {
    openEdit(id);
  }
});

els.list.addEventListener('change', (event) => {
  const target = event.target;
  if (!target.matches('input[data-action="toggle"]')) {
    return;
  }
  toggleTodo(Number(target.dataset.id), target.checked);
});

els.cancelEdit.addEventListener('click', closeEdit);
els.saveEdit.addEventListener('click', saveEdit);
els.modalOverlay.addEventListener('click', (event) => {
  if (event.target === els.modalOverlay) {
    closeEdit();
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && els.modalOverlay.classList.contains('show')) {
    closeEdit();
  }
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    const active = document.activeElement;
    if (active === els.title || active === els.desc) {
      event.preventDefault();
      addTodo();
    }
  }
});

loadTodos();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("company_portal:app", host="0.0.0.0", port=8000, reload=True)
