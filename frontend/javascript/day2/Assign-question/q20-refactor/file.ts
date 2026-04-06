// =======================
// Enums & Interfaces
// =======================

enum UserRole {
    Admin = "Admin",
    User = "User",
    Guest = "Guest"
}

interface User {
    id: string;
    name: string;
    email: string;
    role: UserRole;
    createdAt: Date;
}

interface FilterCriteria {
    name?: string;
    email?: string;
    role?: UserRole;
}

type SortableField = keyof User;
type SortOrder = "asc" | "desc";


// =======================
// Utility Function
// =======================

function generateId(): string {
    return "USR-" + Math.random().toString(36).substring(2, 9);
}


// =======================
// Core Functions
// =======================

function createUser(
    name: string,
    email: string,
    role: UserRole
): User {
    return {
        id: generateId(),
        name,
        email,
        role,
        createdAt: new Date()
    };
}


function updateUser(
    user: User,
    updates: Partial<Omit<User, "id" | "createdAt">>
): User {
    return {
        ...user,
        ...updates
    };
}


function filterUsers(
    users: User[],
    criteria: FilterCriteria
): User[] {
    return users.filter(user => {
        return (
            (!criteria.name || user.name.includes(criteria.name)) &&
            (!criteria.email || user.email.includes(criteria.email)) &&
            (!criteria.role || user.role === criteria.role)
        );
    });
}


function sortUsers(
    users: User[],
    sortBy: SortableField,
    order: SortOrder
): User[] {
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
    constructor(message: string) {
        super(message);
        this.name = "FetchError";
    }
}

async function fetchUsers(
    page: number,
    limit: number
): Promise<User[]> {
    if (page <= 0 || limit <= 0) {
        throw new FetchError("Invalid pagination parameters");
    }

    // Simulated API response
    return new Promise((resolve) => {
        setTimeout(() => {
            const users: User[] = [
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
    private users: User[] = [];
    private cache: Record<string, User> = {};

    async getUser(id: string): Promise<User | undefined> {
        if (this.cache[id]) {
            return this.cache[id];
        }

        const user = this.users.find(u => u.id === id);
        if (user) {
            this.cache[id] = user;
        }

        return user;
    }

    addUser(name: string, email: string, role: UserRole): User {
        const user = createUser(name, email, role);
        this.users.push(user);
        this.cache[user.id] = user;
        return user;
    }

    searchUsers(query: string): User[] {
        return this.users.filter(user =>
            user.name.toLowerCase().includes(query.toLowerCase()) ||
            user.email.toLowerCase().includes(query.toLowerCase())
        );
    }

    getAllUsers(): User[] {
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