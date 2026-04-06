"use strict";
// =======================
// Utility Types (Omit, Pick, Partial)
// =======================
// =======================
// Order + Enum
// =======================
var OrderStatus;
(function (OrderStatus) {
    OrderStatus["Pending"] = "Pending";
    OrderStatus["Processing"] = "Processing";
    OrderStatus["Shipped"] = "Shipped";
    OrderStatus["Delivered"] = "Delivered";
    OrderStatus["Cancelled"] = "Cancelled";
})(OrderStatus || (OrderStatus = {}));
// =======================
// Utility Function (Order ID)
// =======================
function generateOrderId() {
    return "ORD-" + Math.random().toString(36).substring(2, 9);
}
// =======================
// Type Guards
// =======================
function isProduct(value) {
    return (typeof value === "object" &&
        value !== null &&
        "id" in value &&
        "name" in value &&
        "price" in value &&
        "stock" in value);
}
function isOrder(value) {
    return (typeof value === "object" &&
        value !== null &&
        "id" in value &&
        "items" in value &&
        "total" in value &&
        "status" in value);
}
// =======================
// Cart Class
// =======================
class Cart {
    items = [];
    addItem(product, quantity) {
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
        }
        else {
            this.items.push({ product, quantity });
        }
    }
    removeItem(productId) {
        this.items = this.items.filter(i => i.product.id !== productId);
    }
    updateQuantity(productId, quantity) {
        if (quantity <= 0) {
            throw new Error("Quantity must be positive");
        }
        const item = this.items.find(i => i.product.id === productId);
        if (!item)
            throw new Error("Item not found");
        if (quantity > item.product.stock) {
            throw new Error("Not enough stock");
        }
        item.quantity = quantity;
    }
    getTotal() {
        return this.items.reduce((total, item) => total + item.product.price * item.quantity, 0);
    }
    getItemCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    }
    checkout(address) {
        if (this.items.length === 0) {
            throw new Error("Cart is empty");
        }
        // Validate stock again before checkout
        for (const item of this.items) {
            if (item.quantity > item.product.stock) {
                throw new Error(`Insufficient stock for ${item.product.name}`);
            }
        }
        const order = {
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
const product = {
    id: "p1",
    name: "Laptop",
    price: 999,
    category: "Electronics",
    stock: 10
};
// Add item
cart.addItem(product, 2);
console.log(cart.getTotal()); // 1998
console.log(cart.getItemCount()); // 2
// Update quantity
cart.updateQuantity("p1", 3);
console.log(cart.getTotal()); // 2997
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
console.log(order.total); // 1998
// Type Guards Usage
const unknownValue = order;
if (isOrder(unknownValue)) {
    console.log("Valid Order with ID:", unknownValue.id);
}
