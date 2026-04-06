// =======================
// Utility Types (Omit, Pick, Partial)
// =======================

interface Product {
    id: string;
    name: string;
    price: number;
    category: string;
    stock: number;
}

// API Variations
type CreateProduct = Omit<Product, "id">;
type UpdateProduct = Partial<Product>;
type ProductSummary = Pick<Product, "id" | "name" | "price">;


// =======================
// CartItem & Address
// =======================

interface CartItem {
    product: Product;
    quantity: number;
}

interface Address {
    street: string;
    city: string;
    zip: string;
    country: string;
}


// =======================
// Order + Enum
// =======================

enum OrderStatus {
    Pending = "Pending",
    Processing = "Processing",
    Shipped = "Shipped",
    Delivered = "Delivered",
    Cancelled = "Cancelled"
}

interface Order {
    id: string;
    items: CartItem[];
    total: number;
    status: OrderStatus;
    shippingAddress: Address;
}


// =======================
// Utility Function (Order ID)
// =======================

function generateOrderId(): string {
    return "ORD-" + Math.random().toString(36).substring(2, 9);
}


// =======================
// Type Guards
// =======================

function isProduct(value: unknown): value is Product {
    return (
        typeof value === "object" &&
        value !== null &&
        "id" in value &&
        "name" in value &&
        "price" in value &&
        "stock" in value
    );
}

function isOrder(value: unknown): value is Order {
    return (
        typeof value === "object" &&
        value !== null &&
        "id" in value &&
        "items" in value &&
        "total" in value &&
        "status" in value
    );
}


// =======================
// Cart Class
// =======================

class Cart {
    private items: CartItem[] = [];

    addItem(product: Product, quantity: number): void {
        if (quantity <= 0) {
            throw new Error("Quantity must be positive");
        }

        if (quantity > product.stock) {
            throw new Error("Not enough stock available");
        }

        const existingItem = this.items.find(i => i.product.id === product.id);

        if (existingItem) {
            if (existingItem.quantity + quantity > product.stock) {
                throw new Error("Exceeds stock limit");
            }
            existingItem.quantity += quantity;
        } else {
            this.items.push({ product, quantity });
        }
    }

    removeItem(productId: string): void {
        this.items = this.items.filter(i => i.product.id !== productId);
    }

    updateQuantity(productId: string, quantity: number): void {
        if (quantity <= 0) {
            throw new Error("Quantity must be positive");
        }

        const item = this.items.find(i => i.product.id === productId);
        if (!item) throw new Error("Item not found");

        if (quantity > item.product.stock) {
            throw new Error("Not enough stock");
        }

        item.quantity = quantity;
    }

    getTotal(): number {
        return this.items.reduce(
            (total, item) => total + item.product.price * item.quantity,
            0
        );
    }

    getItemCount(): number {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    }

    checkout(address: Address): Order {
        if (this.items.length === 0) {
            throw new Error("Cart is empty");
        }

        // Validate stock again before checkout
        for (const item of this.items) {
            if (item.quantity > item.product.stock) {
                throw new Error(`Insufficient stock for ${item.product.name}`);
            }
        }

        const order: Order = {
            id: generateOrderId(),
            items: [...this.items],
            total: this.getTotal(),
            status: OrderStatus.Pending,
            shippingAddress: address
        };

        // Reduce stock after checkout
        this.items.forEach(item => {
            item.product.stock -= item.quantity;
        });

        // Clear cart
        this.items = [];

        return order;
    }
}


// =======================
// Usage Examples
// =======================

const cart = new Cart();

const product: Product = {
    id: "p1",
    name: "Laptop",
    price: 999,
    category: "Electronics",
    stock: 10
};

// Add item
cart.addItem(product, 2);

console.log(cart.getTotal());     // 1998
console.log(cart.getItemCount()); // 2

// Update quantity
cart.updateQuantity("p1", 3);
console.log(cart.getTotal());     // 2997

// Remove item
cart.removeItem("p1");
console.log(cart.getItemCount()); // 0

// Add again for checkout
cart.addItem(product, 2);

const order = cart.checkout({
    street: "123 Main",
    city: "NYC",
    zip: "10001",
    country: "US"
});

console.log(order.status); // Pending
console.log(order.total);  // 1998

// Type Guards Usage
const unknownValue: unknown = order;

if (isOrder(unknownValue)) {
    console.log("Valid Order with ID:", unknownValue.id);
}