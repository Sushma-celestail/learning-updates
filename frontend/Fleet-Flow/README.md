# 🌐 Fleet-Flow: Advanced Warehouse & Logistics Management System

Fleet-Flow is a high-fidelity, enterprise-grade Warehouse Management System (WMS) designed to streamline global supply chain operations. It provides a real-time bridge between administration, warehouse hubs, and field drivers.

## 🚀 Key Features Implemented

### 👔 Administrative & Hub Management
*   **Infrastructure Control**: Register and decommission distribution hubs with **Live Google Maps Integration** for geographic verification.
*   **Personnel Access Control**: Comprehensive CRUD (Create, Read, Update, Delete) operations for team members with Role-Based Access Control (RBAC).
*   **Intelligent Onboarding**: Zero-default registration flow with strict validation for mandatory security credentials and hub assignments.

### 📊 Real-Time Operations Dashboard
*   **Inventory Insights**: Visual tracking of stock levels and pending approvals with interactive trend toggles (Weekly/Monthly).
*   **Global Activity Log**: Centralized event history with unique transaction IDs and status tracking.
*   **Notification Engine**: Dynamic alerting system for critical stock levels, system updates, and logistics events.

### 🚚 Logistics & Driver Ecosystem
*   **Scoped Tracking**: Role-aware views ensuring Drivers see only their assigned missions, while Managers oversee entire territories.
*   **Live Transit Updates**: Mobile-responsive status transitions (Pending -> In Transit -> Delivered) with immediate backend synchronization.
*   **Hub Connectivity**: Every driver is bonded to a "Home Base Hub," aligning the digital model with physical logistics standards.

### 💎 Premium User Experience
*   **Kinetic UI/UX**: Built with React 19, Tailwind CSS, and Framer Motion for a fluid, glassmorphic design.
*   **Interactive Toast System**: Replaced browser defaults with custom, high-fidelity notifications and confirmation dialogs.
*   **Robust Backend**: Powered by FastAPI and SQLAlchemy with a clean **Repository-Service-Schema** architecture.

---

## 🛠️ Technical Stack

- **Frontend**: React 19, Vite, Tailwind CSS, Lucide Icons, Zod, React Hook Form, React Hot Toast.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Pydantic, JWT Authentication.
- **Tools**: Google Maps API Embed, Recharts.

---

## 🔮 Future Roadmap (Business Logic Extensions)

To further scale Fleet-Flow into an industrial powerhouse, the following business logic layers are planned:

### 1. 🏗️ Intelligent WMS+
*   **Capacity Logic**: Automatic blocking of incoming shipments when a hub reaches its volume limit.
*   **Bin/Rack Mapping**: Granular item tracking down to specific zones and shelf levels.
*   **Low-Stock Triggers**: Automated restock request generation based on AI-predicted thresholds.

### 2. 🚛 Logistics 2.0
*   **Routing Optimization**: Multi-hub pathfinding to reduce fuel consumption and transit time.
*   **Load Batching**: Grouping multiple shipments into a single truckload for better fleet utilization.
*   **ePOD (Electronic Proof of Delivery)**: Mandatory digital signature and photo verification for final mile delivery.

### 💰 Financial & Compliance Layer
*   **Automated Invoicing**: Generation of PDF billing records upon successful delivery.
*   **Inventory Valuation**: Real-time COGS (Cost of Goods Sold) calculation for global stock.
*   **Audit Trail**: Immutable database-level history of every system modification for enterprise compliance.

### 📡 Connectivity
*   **Real-time WebSockets**: Instant dashboard updates without page refreshes.
*   **Mobile Push Notifications**: Direct alerts to Driver mobile devices for new assignments.

---

## 📥 Installation

### Backend
```bash
cd BACKEND
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd FRONTEND
npm install
npm run dev
```

---
*Developed with focus on Kinetic Design and Operational Excellence.*
