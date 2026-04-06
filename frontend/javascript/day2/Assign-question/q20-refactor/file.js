"use strict";
// =======================
// Enums & Interfaces
// =======================
var UserRole;
(function (UserRole) {
    UserRole["Admin"] = "Admin";
    UserRole["User"] = "User";
    UserRole["Guest"] = "Guest";
})(UserRole || (UserRole = {}));
// =======================
// Utility Function
// =======================
function generateId() {
    return "USR-" + Math.random().toString(36).substring(2, 9);
}
// =======================
// Core Functions
// =======================
function createUser(name, email, role) {
    return {
        id: generateId(),
        name,
        email,
        role,
        createdAt: new Date()
    };
}
function updateUser(user, updates) {
    return {
        ...user,
        ...updates
    };
}
function filterUsers(users, criteria) {
    return users.filter(user => {
        return ((!criteria.name || user.name.includes(criteria.name)) &&
            (!criteria.email || user.email.includes(criteria.email)) &&
            (!criteria.role || user.role === criteria.role));
    });
}
function sortUsers(users, sortBy, order) {
    return [...users].sort((a, b) => {
        const valA = a[sortBy];
        const valB = b[sortBy];
        if (valA instanceof Date && valB instanceof Date) {
            return order === "asc"
                ? valA.getTime() - valB.getTime()
                : valB.getTime() - valA.getTime();
        }
        if (typeof valA === "string" && typeof valB === "string") {
            return order === "asc"
                ? valA.localeCompare(valB)
                : valB.localeCompare(valA);
        }
        return 0;
    });
}
// =======================
// Async Fetch Function
// =======================
class FetchError extends Error {
    constructor(message) {
        super(message);
        this.name = "FetchError";
    }
}
async function fetchUsers(page, limit) {
    if (page <= 0 || limit <= 0) {
        throw new FetchError("Invalid pagination parameters");
    }
    // Simulated API response
    return new Promise((resolve) => {
        setTimeout(() => {
            const users = [
                createUser("Alice", "alice@example.com", UserRole.Admin),
                createUser("Bob", "bob@example.com", UserRole.User)
            ];
            resolve(users);
        }, 500);
    });
}
// =======================
// UserService Class
// =======================
class UserService {
    users = [];
    cache = {};
    async getUser(id) {
        if (this.cache[id]) {
            return this.cache[id];
        }
        const user = this.users.find(u => u.id === id);
        if (user) {
            this.cache[id] = user;
        }
        return user;
    }
    addUser(name, email, role) {
        const user = createUser(name, email, role);
        this.users.push(user);
        this.cache[user.id] = user;
        return user;
    }
    searchUsers(query) {
        return this.users.filter(user => user.name.toLowerCase().includes(query.toLowerCase()) ||
            user.email.toLowerCase().includes(query.toLowerCase()));
    }
    getAllUsers() {
        return [...this.users];
    }
}
// =======================
// Usage Examples
// =======================
const service = new UserService();
const u1 = service.addUser("Alice", "alice@mail.com", UserRole.Admin);
const u2 = service.addUser("Bob", "bob@mail.com", UserRole.User);
console.log(service.getAllUsers());
const updated = updateUser(u1, { name: "Alice Updated" });
console.log(updated);
// Filter
const filtered = filterUsers(service.getAllUsers(), { role: UserRole.Admin });
console.log(filtered);
// Sort
const sorted = sortUsers(service.getAllUsers(), "name", "asc");
console.log(sorted);
// Fetch
fetchUsers(1, 10)
    .then(users => console.log(users))
    .catch(err => console.error(err.message));
