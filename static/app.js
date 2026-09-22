// ============================================
// app.js - Hostel Management System Frontend
// ============================================

const API = 'http://localhost:5000/api';
let token = localStorage.getItem('hms_token');
let allStudents = [], allRooms = [], allHostels = [];

// ---- Auth Guard ----
if (!token) { window.location.href = '/login.html'; }

const admin = JSON.parse(localStorage.getItem('hms_admin') || '{}');
document.getElementById('admin-name').textContent = admin.name || 'Admin';
const initial = (admin.name || 'A')[0].toUpperCase();
document.querySelector('.admin-avatar').textContent = initial;

function logout() {
    localStorage.removeItem('hms_token');
    localStorage.removeItem('hms_admin');
    window.location.href = '/login.html';
}

// ---- Fetch Helper ----
async function api(method, path, body) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + path, opts);
    const data = await res.json();
    if (res.status === 401) { logout(); }
    return { ok: res.ok, data, status: res.status };
}

// ---- Toast ----
function toast(msg, type = 'success') {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = `toast ${type} show`;
    setTimeout(() => t.classList.remove('show'), 3000);
}

// ---- Modal ----
function openModal(id) {
    document.getElementById(id).classList.add('open');
}
function closeModal(id) {
    document.getElementById(id).classList.remove('open');
}
document.querySelectorAll('.modal-overlay').forEach(m => {
    m.addEventListener('click', e => { if (e.target === m) m.classList.remove('open'); });
});

// ---- Clock ----
function updateClock() {
    document.getElementById('current-time').textContent =
        new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}
setInterval(updateClock, 1000); updateClock();

// ---- Navigation ----
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        const page = item.dataset.page;
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        item.classList.add('active');
        document.getElementById('page-' + page).classList.add('active');
        document.getElementById('page-title').textContent = item.textContent.trim();
        loadPage(page);
    });
});

function loadPage(page) {
    if (page === 'dashboard') loadDashboard();
    else if (page === 'students') loadStudents();
    else if (page === 'hostels') loadHostels();
    else if (page === 'rooms') { loadRooms(); loadAllocations(); populateHostelDropdowns(); }
    else if (page === 'visitors') { loadVisitors(); populateStudentDropdownsFromAPI(); }
    else if (page === 'furniture') { loadRooms().then(() => loadFurniture()); }
}

// ---- Inner Tabs (Rooms) ----
function switchInnerTab(id, btn) {
    document.querySelectorAll('.inner-tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.inner-tab').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');
}

// ============================================
// DASHBOARD
// ============================================
async function loadDashboard() {
    const { ok, data } = await api('GET', '/dashboard/stats');
    if (!ok) return;
    document.getElementById('stat-students').textContent = data.total_students;
    document.getElementById('stat-rooms').textContent = data.total_rooms;
    document.getElementById('stat-hostels').textContent = data.total_hostels;
    document.getElementById('stat-visitors').textContent = data.total_visitors;

    const tbody = document.getElementById('recent-visitors-body');
    if (data.recent_visitors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No visitors yet</td></tr>';
        return;
    }
    tbody.innerHTML = data.recent_visitors.map(v => `
        <tr>
            <td><strong>${v.visitor_name}</strong></td>
            <td>${v.student_name || '—'}</td>
            <td>${v.visit_date}</td>
            <td>${v.in_time}</td>
            <td>${v.out_time ? v.out_time : '<span class="badge badge-yellow">Active</span>'}</td>
        </tr>
    `).join('');
}

// ============================================
// STUDENTS
// ============================================
async function loadStudents(search = '', dept = '') {
    let url = `/students/?search=${encodeURIComponent(search)}&dept=${encodeURIComponent(dept)}`;
    const { ok, data } = await api('GET', url);
    if (!ok) return;
    allStudents = data;
    renderStudents(data);
    populateStudentDropdowns();
}

function renderStudents(students) {
    const tbody = document.getElementById('students-body');
    if (!students.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No students found</td></tr>';
        return;
    }
    tbody.innerHTML = students.map(s => `
        <tr>
            <td><span class="badge badge-gray">#${s.student_id}</span></td>
            <td><strong>${s.fname} ${s.lname}</strong></td>
            <td>${s.mob_no}</td>
            <td>${s.dept}</td>
            <td>Year ${s.year_of_study}</td>
            <td>${s.hostel_name || '<span class="badge badge-gray">Unassigned</span>'}</td>
            <td>
                <button class="btn-sm btn-edit" onclick="editStudent(${s.student_id})">Edit</button>
                <button class="btn-sm btn-delete" onclick="deleteStudent(${s.student_id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function searchStudents() {
    const search = document.getElementById('student-search').value;
    const dept = document.getElementById('student-filter-dept').value;
    loadStudents(search, dept);
}

async function saveStudent() {
    const id = document.getElementById('student-id').value;
    const payload = {
        fname: document.getElementById('s-fname').value.trim(),
        lname: document.getElementById('s-lname').value.trim(),
        mob_no: document.getElementById('s-mob').value.trim(),
        dept: document.getElementById('s-dept').value,
        year_of_study: document.getElementById('s-year').value,
        hostel_id: document.getElementById('s-hostel').value || null
    };
    if (!payload.fname || !payload.lname || !payload.mob_no || !payload.dept || !payload.year_of_study)
        return toast('Please fill all required fields', 'error');

    const method = id ? 'PUT' : 'POST';
    const path = id ? `/students/${id}` : '/students/';
    const { ok, data } = await api(method, path, payload);
    if (ok) { toast(id ? 'Student updated!' : 'Student added!'); closeModal('modal-student'); loadStudents(); }
    else toast(data.error || 'Failed', 'error');
}

async function editStudent(id) {
    const s = allStudents.find(x => x.student_id === id);
    if (!s) return;
    document.getElementById('student-id').value = s.student_id;
    document.getElementById('student-modal-title').textContent = 'Edit Student';
    document.getElementById('s-fname').value = s.fname;
    document.getElementById('s-lname').value = s.lname;
    document.getElementById('s-mob').value = s.mob_no;
    document.getElementById('s-dept').value = s.dept;
    document.getElementById('s-year').value = s.year_of_study;
    document.getElementById('s-hostel').value = s.hostel_id || '';
    openModal('modal-student');
}

async function deleteStudent(id) {
    if (!confirm('Delete this student?')) return;
    const { ok, data } = await api('DELETE', `/students/${id}`);
    if (ok) { toast('Student deleted'); loadStudents(); }
    else toast(data.error || 'Failed', 'error');
}

function resetStudentModal() {
    document.getElementById('student-id').value = '';
    document.getElementById('student-modal-title').textContent = 'Add Student';
    ['s-fname','s-lname','s-mob'].forEach(id => document.getElementById(id).value = '');
    ['s-dept','s-year','s-hostel'].forEach(id => document.getElementById(id).value = '');
}

// ============================================
// HOSTELS
// ============================================
async function loadHostels() {
    const { ok, data } = await api('GET', '/hostels/');
    if (!ok) return;
    allHostels = data;
    const grid = document.getElementById('hostels-grid');
    if (!data.length) {
        grid.innerHTML = '<div class="loading-cell">No hostels found</div>';
        return;
    }
    grid.innerHTML = data.map(h => `
        <div class="hostel-card">
            <div class="hostel-card-title">${h.hostel_name}</div>
            <div class="hostel-stats">
                <div class="hostel-stat">
                    <div class="hostel-stat-val">${h.no_of_rooms}</div>
                    <div class="hostel-stat-lbl">Rooms</div>
                </div>
                <div class="hostel-stat">
                    <div class="hostel-stat-val">${h.no_of_students}</div>
                    <div class="hostel-stat-lbl">Students</div>
                </div>
            </div>
            <div class="hostel-admin">👤 ${h.admin_name || 'No admin assigned'}</div>
            <div class="hostel-actions">
                <button class="btn-sm btn-delete" onclick="deleteHostel(${h.hostel_id})">Delete</button>
            </div>
        </div>
    `).join('');
    populateHostelDropdowns();
}

async function saveHostel() {
    const payload = {
        hostel_name: document.getElementById('h-name').value.trim(),
        no_of_rooms: document.getElementById('h-rooms').value,
        admin_id: document.getElementById('h-admin').value || null
    };
    if (!payload.hostel_name || !payload.no_of_rooms)
        return toast('Name and room count required', 'error');
    const { ok, data } = await api('POST', '/hostels/', payload);
    if (ok) { toast('Hostel added!'); closeModal('modal-hostel'); loadHostels(); }
    else toast(data.error || 'Failed', 'error');
}

async function deleteHostel(id) {
    if (!confirm('Delete this hostel?')) return;
    const { ok, data } = await api('DELETE', `/hostels/${id}`);
    if (ok) { toast('Hostel deleted'); loadHostels(); }
    else toast(data.error || 'Failed', 'error');
}

// ============================================
// ROOMS
// ============================================
async function loadRooms() {
    const hostel_id = document.getElementById('room-filter-hostel')?.value || '';
    const { ok, data } = await api('GET', `/rooms/?hostel_id=${hostel_id}`);
    if (!ok) return;
    allRooms = data;
    const tbody = document.getElementById('rooms-body');
    if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No rooms found</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(r => {
        const isFull = r.occupied >= r.capacity;
        return `
        <tr>
            <td><span class="badge badge-gray">#${r.room_id}</span></td>
            <td><strong>Room ${r.room_no}</strong></td>
            <td>${r.hostel_name || '—'}</td>
            <td>${r.capacity}</td>
            <td>${r.occupied}</td>
            <td><span class="badge ${isFull ? 'badge-red' : 'badge-green'}">${isFull ? 'Full' : 'Available'}</span></td>
            <td><button class="btn-sm btn-delete" onclick="deleteRoom(${r.room_id})">Delete</button></td>
        </tr>`;
    }).join('');
    populateRoomDropdowns();
}

async function saveRoom() {
    const payload = {
        room_no: document.getElementById('r-no').value.trim(),
        hostel_id: document.getElementById('r-hostel').value,
        capacity: document.getElementById('r-cap').value || 2
    };
    if (!payload.room_no || !payload.hostel_id)
        return toast('Room number and hostel required', 'error');
    const { ok, data } = await api('POST', '/rooms/', payload);
    if (ok) { toast('Room added!'); closeModal('modal-room'); loadRooms(); }
    else toast(data.error || 'Failed', 'error');
}

async function deleteRoom(id) {
    if (!confirm('Delete this room?')) return;
    const { ok, data } = await api('DELETE', `/rooms/${id}`);
    if (ok) { toast('Room deleted'); loadRooms(); }
    else toast(data.error || 'Failed', 'error');
}

async function loadAllocations() {
    const { ok, data } = await api('GET', '/rooms/allocations');
    if (!ok) return;
    const tbody = document.getElementById('allocations-body');
    if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No allocations yet</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(a => `
        <tr>
            <td><strong>${a.student_name}</strong></td>
            <td>${a.dept}</td>
            <td>Room ${a.room_no}</td>
            <td>${a.hostel_name}</td>
            <td><button class="btn-sm btn-delete" onclick="deallocate(${a.stay_id})">Remove</button></td>
        </tr>
    `).join('');
}

async function saveAllocation() {
    const payload = {
        student_id: document.getElementById('alloc-student').value,
        room_id: document.getElementById('alloc-room').value
    };
    if (!payload.student_id || !payload.room_id)
        return toast('Select student and room', 'error');
    const { ok, data } = await api('POST', '/rooms/allocations', payload);
    if (ok) { toast('Room allocated!'); closeModal('modal-allocate'); loadAllocations(); loadRooms(); }
    else toast(data.error || 'Failed', 'error');
}

async function deallocate(id) {
    if (!confirm('Remove this allocation?')) return;
    const { ok } = await api('DELETE', `/rooms/allocations/${id}`);
    if (ok) { toast('Allocation removed'); loadAllocations(); loadRooms(); }
}

// ============================================
// VISITORS
// ============================================
async function loadVisitors() {
    const { ok, data } = await api('GET', '/visitors/');
    if (!ok) return;
    const tbody = document.getElementById('visitors-body');
    if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No visitors yet</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(v => `
        <tr>
            <td><strong>${v.visitor_name}</strong></td>
            <td>${v.student_name || '—'}</td>
            <td>${v.visit_date}</td>
            <td>${v.in_time}</td>
            <td>${v.out_time || '—'}</td>
            <td><span class="badge ${v.out_time ? 'badge-gray' : 'badge-yellow'}">${v.out_time ? 'Left' : 'Active'}</span></td>
            <td><button class="btn-sm btn-delete" onclick="deleteVisitor(${v.visitor_id})">Delete</button></td>
        </tr>
    `).join('');
}

async function saveVisitor() {
    const payload = {
        visitor_name: document.getElementById('v-name').value.trim(),
        student_id: document.getElementById('v-student').value,
        visit_date: document.getElementById('v-date').value,
        in_time: document.getElementById('v-in').value,
        out_time: document.getElementById('v-out').value || null
    };
    if (!payload.visitor_name || !payload.student_id || !payload.visit_date || !payload.in_time)
        return toast('Please fill all required fields', 'error');
    const { ok, data } = await api('POST', '/visitors/', payload);
    if (ok) { toast('Visitor added!'); closeModal('modal-visitor'); loadVisitors(); }
    else toast(data.error || 'Failed', 'error');
}

async function deleteVisitor(id) {
    if (!confirm('Delete this visitor entry?')) return;
    const { ok } = await api('DELETE', `/visitors/${id}`);
    if (ok) { toast('Visitor deleted'); loadVisitors(); }
}

// ============================================
// FURNITURE
// ============================================
async function loadFurniture() {
    const room_id = document.getElementById('furniture-filter-room')?.value || '';
    const { ok, data } = await api('GET', `/furniture/?room_id=${room_id}`);
    if (!ok) return;
    const tbody = document.getElementById('furniture-body');
    if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No furniture found</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(f => `
        <tr>
            <td><span class="badge badge-gray">#${f.furniture_id}</span></td>
            <td>🪑 ${f.furniture_type}</td>
            <td>${f.room_no ? 'Room ' + f.room_no : '—'}</td>
            <td>${f.hostel_name || '—'}</td>
            <td><button class="btn-sm btn-delete" onclick="deleteFurniture(${f.furniture_id})">Delete</button></td>
        </tr>
    `).join('');
}

async function saveFurniture() {
    const payload = {
        furniture_type: document.getElementById('f-type').value,
        room_id: document.getElementById('f-room').value
    };
    if (!payload.furniture_type || !payload.room_id)
        return toast('Select type and room', 'error');
    const { ok, data } = await api('POST', '/furniture/', payload);
    if (ok) { toast('Furniture added!'); closeModal('modal-furniture'); loadFurniture(); }
    else toast(data.error || 'Failed', 'error');
}

async function deleteFurniture(id) {
    if (!confirm('Delete this furniture?')) return;
    const { ok } = await api('DELETE', `/furniture/${id}`);
    if (ok) { toast('Furniture deleted'); loadFurniture(); }
}

// ============================================
// DROPDOWN POPULATORS
// ============================================
async function populateHostelDropdowns() {
    const { ok, data } = await api('GET', '/hostels/');
    if (!ok) return;
    allHostels = data;
    const opts = data.map(h => `<option value="${h.hostel_id}">${h.hostel_name}</option>`).join('');
    ['s-hostel', 'r-hostel'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = `<option value="">Select hostel</option>${opts}`;
    });
    const roomFilter = document.getElementById('room-filter-hostel');
    if (roomFilter) roomFilter.innerHTML = `<option value="">All Hostels</option>${opts}`;
}

async function populateStudentDropdowns() {
    // Use cached allStudents (already loaded on students page)
    const opts = allStudents.map(s => `<option value="${s.student_id}">${s.fname} ${s.lname}</option>`).join('');
    ['v-student', 'alloc-student'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = `<option value="">Select student</option>${opts}`;
    });
}

async function populateStudentDropdownsFromAPI() {
    // Always fetch fresh from API (used when students page wasn't visited first)
    const { ok, data } = await api('GET', '/students/');
    if (!ok) return;
    allStudents = data;
    await populateStudentDropdowns();
}

async function populateRoomDropdowns() {
    // Always fetch fresh rooms from API so newly added rooms/hostels appear
    const { ok, data } = await api('GET', '/rooms/');
    if (!ok) return;
    allRooms = data;
    const opts = data.map(r => `<option value="${r.room_id}">Room ${r.room_no} – ${r.hostel_name}</option>`).join('');
    ['alloc-room', 'f-room'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = `<option value="">Select room</option>${opts}`;
    });
    const furnitureFilter = document.getElementById('furniture-filter-room');
    if (furnitureFilter) furnitureFilter.innerHTML = `<option value="">All Rooms</option>${opts}`;
}

async function populateHostelFilter() {
    await populateHostelDropdowns();
}

async function populateAdminDropdown() {
    // For simplicity, we pre-fill current admin
    const el = document.getElementById('h-admin');
    if (el && admin.id) {
        el.innerHTML = `<option value="${admin.id}">${admin.name}</option>`;
    }
}

// ============================================
// MODAL OPEN HOOKS (reset + populate)
// ============================================
document.getElementById('modal-student').addEventListener('click', () => {});
document.querySelector('[onclick="openModal(\'modal-student\')"]')?.addEventListener('click', () => {
    resetStudentModal();
    populateHostelDropdowns();
});

// Re-wire Add buttons: always fetch fresh data before opening each modal
document.querySelectorAll('.btn-add').forEach(btn => {
    const modalId = btn.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
    if (!modalId) return;
    btn.addEventListener('click', async () => {
        if (modalId === 'modal-student') {
            resetStudentModal();
            await populateHostelDropdowns();
        }
        if (modalId === 'modal-hostel') {
            await populateAdminDropdown();
        }
        if (modalId === 'modal-room') {
            await populateHostelDropdowns(); // always fresh
        }
        if (modalId === 'modal-allocate') {
            await populateStudentDropdownsFromAPI();
            await populateRoomDropdowns(); // always fresh
        }
        if (modalId === 'modal-visitor') {
            await populateStudentDropdownsFromAPI();
        }
        if (modalId === 'modal-furniture') {
            await populateRoomDropdowns(); // always fresh — picks up new hostels/rooms
        }
    });
});

// ============================================
// INIT
// ============================================
loadDashboard();
