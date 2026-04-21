# 📦 Precision Flow | Warehouse Management System

Precision Flow is a premium, high-fidelity Warehouse Management System (WMS) built to manage global logistics with a focus on professional UI/UX and role-based operational efficiency.

## 🚀 Technology Stack

- **Frontend**: React 19 + TypeScript
- **Styling**: Tailwind CSS 4.0 (Engineered for modern aesthetics)
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **State Management**: React Context API
- **Networking**: Axios with JWT Interceptor

---

## 🔐 Testing Credentials

For demonstration and sandbox testing, the following pre-configured credentials can be used. Each role provides access to specific dashboards and features as per the operational requirements.

| Role | Email Address | Password | Description |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@gmail.com` | `Pass@123` | Full system access, users, and warehouses |
| **Manager** | `manager@gmail.com` | `Pass@123` | Inventory approvals and shipment monitoring |
| **Clerk** | `clerk@gmail.com` | `Pass@123` | Inventory entry and shipment creation |
| **Driver** | `driver@gmail.com` | `Pass@123` | My Shipments dashboard and status updates |

> [!TIP]
> You can also use the **Quick Launch** buttons at the bottom of the Login Page to jump into any role instantly.

---

## 🛠️ Project Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```

3. **Environment Configuration**:
   The application points to `http://localhost:8000` by default. You can change this in the `.env` file.

---

## 📁 Key Directories

- `src/api`: Modularized API logic for all modules.
- `src/components/ui`: Premium, reusable UI/UX primitives (Glassmorphism cards, interactive buttons).
- `src/context`: Auth state management and role guarding.
- `src/pages`: Role-aware dashboard implementations.
- `src/types`: Consolidated TypeScript interfaces.
