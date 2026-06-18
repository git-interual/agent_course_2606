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
<title>할일 관리</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; min-height: 100vh; padding: 32px 16px; }
  h1 { text-align: center; color: #1a73e8; margin-bottom: 24px; font-size: 1.8rem; }
  .container { max-width: 640px; margin: 0 auto; }
  .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }
  .card h2 { font-size: 1rem; color: #555; margin-bottom: 12px; }
  input[type=text], textarea {
    width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 8px;
    font-size: 0.95rem; margin-bottom: 8px; outline: none;
  }
  input[type=text]:focus, textarea:focus { border-color: #1a73e8; }
  textarea { resize: vertical; height: 64px; }
  .btn { padding: 8px 18px; border: none; border-radius: 8px; cursor: pointer; font-size: 0.9rem; }
  .btn-primary { background: #1a73e8; color: white; }
  .btn-primary:hover { background: #1558b0; }
  .btn-danger { background: #e53935; color: white; }
  .btn-danger:hover { background: #b71c1c; }
  .btn-success { background: #43a047; color: white; }
  .btn-success:hover { background: #2e7d32; }
  .btn-edit { background: #fb8c00; color: white; }
  .btn-edit:hover { background: #e65100; }
  #todo-list { list-style: none; }
  #todo-list li {
    background: white; border-radius: 10px; padding: 14px 16px;
    margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    display: flex; align-items: flex-start; gap: 12px;
  }
  #todo-list li.done .todo-title { text-decoration: line-through; color: #aaa; }
  .todo-body { flex: 1; }
  .todo-title { font-size: 1rem; font-weight: 600; color: #333; }
  .todo-desc { font-size: 0.85rem; color: #777; margin-top: 2px; }
  .todo-actions { display: flex; gap: 6px; flex-shrink: 0; }
  input[type=checkbox] { width: 18px; height: 18px; margin-top: 3px; cursor: pointer; accent-color: #1a73e8; }
  .empty { text-align: center; color: #bbb; padding: 20px 0; font-size: 0.95rem; }
  /* 수정 모달 */
  #modal-overlay {
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4);
    justify-content: center; align-items: center; z-index: 100;
  }
  #modal-overlay.show { display: flex; }
  #modal {
    background: white; border-radius: 12px; padding: 24px; width: 90%; max-width: 400px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }
  #modal h2 { margin-bottom: 16px; font-size: 1.1rem; color: #333; }
  .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
</style>
</head>
<body>
<div class="container">
  <h1>📝 할일 관리</h1>

  <div class="card">
    <h2>새 할일 추가</h2>
    <input type="text" id="new-title" placeholder="할일 제목 *" />
    <textarea id="new-desc" placeholder="설명 (선택)"></textarea>
    <button class="btn btn-primary" onclick="addTodo()">추가</button>
  </div>

  <div class="card">
    <h2>할일 목록</h2>
    <ul id="todo-list"><li class="empty">할일이 없습니다.</li></ul>
  </div>
</div>

<!-- 수정 모달 -->
<div id="modal-overlay">
  <div id="modal">
    <h2>할일 수정</h2>
    <input type="hidden" id="edit-id" />
    <input type="text" id="edit-title" placeholder="제목" />
    <textarea id="edit-desc" placeholder="설명"></textarea>
    <div class="modal-actions">
      <button class="btn" style="background:#eee;color:#333" onclick="closeModal()">취소</button>
      <button class="btn btn-primary" onclick="saveEdit()">저장</button>
    </div>
  </div>
</div>

<script>
async function loadTodos() {
  const res = await fetch('/todos');
  const todos = await res.json();
  const list = document.getElementById('todo-list');
  if (todos.length === 0) {
    list.innerHTML = '<li class="empty">할일이 없습니다.</li>';
    return;
  }
  list.innerHTML = todos.map(t => `
    <li id="item-${t.id}" class="${t.done ? 'done' : ''}">
      <input type="checkbox" ${t.done ? 'checked' : ''} onchange="toggleDone(${t.id}, this.checked)" />
      <div class="todo-body">
        <div class="todo-title">${escHtml(t.title)}</div>
        ${t.description ? `<div class="todo-desc">${escHtml(t.description)}</div>` : ''}
      </div>
      <div class="todo-actions">
        <button class="btn btn-edit" onclick="openEdit(${t.id}, '${escAttr(t.title)}', '${escAttr(t.description || '')}')">수정</button>
        <button class="btn btn-danger" onclick="deleteTodo(${t.id})">삭제</button>
      </div>
    </li>
  `).join('');
}

async function addTodo() {
  const title = document.getElementById('new-title').value.trim();
  if (!title) { alert('제목을 입력하세요.'); return; }
  const desc = document.getElementById('new-desc').value.trim();
  await fetch('/todos', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ title, description: desc || null })
  });
  document.getElementById('new-title').value = '';
  document.getElementById('new-desc').value = '';
  loadTodos();
}

async function deleteTodo(id) {
  if (!confirm('삭제하시겠습니까?')) return;
  await fetch(`/todos/${id}`, { method: 'DELETE' });
  loadTodos();
}

async function toggleDone(id, done) {
  await fetch(`/todos/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ done })
  });
  loadTodos();
}

function openEdit(id, title, desc) {
  document.getElementById('edit-id').value = id;
  document.getElementById('edit-title').value = title;
  document.getElementById('edit-desc').value = desc;
  document.getElementById('modal-overlay').classList.add('show');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('show');
}

async function saveEdit() {
  const id = document.getElementById('edit-id').value;
  const title = document.getElementById('edit-title').value.trim();
  const desc = document.getElementById('edit-desc').value.trim();
  if (!title) { alert('제목을 입력하세요.'); return; }
  await fetch(`/todos/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ title, description: desc || null })
  });
  closeModal();
  loadTodos();
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escAttr(str) {
  return str.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
}

document.getElementById('new-title').addEventListener('keydown', e => {
  if (e.key === 'Enter') addTodo();
});

loadTodos();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("company_portal:app", host="0.0.0.0", port=8000, reload=True)
