import { Customer, ProductGroup, Product, Order, Warehouse, StockItem, StockTransaction, User } from "./types";

export const DEFAULT_USER: User = {
  username: "admin",
  full_name: "مدیر سیستم حاما",
  email: "admin@hamatextile.com"
};

export const DEFAULT_CUSTOMERS: Customer[] = [
  { id: "c1", customer_code: "C-101", name: "علی", last_name: "رضایی", phone_number: "09121111111" },
  { id: "c2", customer_code: "C-102", name: "مریم", last_name: "احمدی", phone_number: "09122222222" },
  { id: "c3", customer_code: "C-103", name: "جواد", last_name: "کریمی", phone_number: "09123333333" }
];

export const DEFAULT_GROUPS: ProductGroup[] = [
  { id: "g1", name: "پارچه نخی" },
  { id: "g2", name: "پارچه پشمی" },
  { id: "g3", name: "پارچه ابریشمی" }
];

export const DEFAULT_PRODUCTS: Product[] = [
  { id: "p1", code: "P-201", group_id: "g1", name: "پارچه تترون سفید", unit: "عدد", initial_stock: 50, unit_price: 120000, description: "مناسب برای پیراهن و ملحفه" },
  { id: "p2", code: "P-202", group_id: "g1", name: "پارچه کتان سرمه‌ای", unit: "کیلوگرم", initial_stock: 100, unit_price: 250000, description: "کتان ضخیم مناسب شلوار" },
  { id: "p3", code: "P-203", group_id: "g2", name: "پارچه فاستونی طوسی", unit: "عدد", initial_stock: 30, unit_price: 450000, description: "مناسب کت و شلوار مجلسی" }
];

export const DEFAULT_WAREHOUSES: Warehouse[] = [
  { id: "w1", name: "انبار مواد اولیه مرکزی", code: "W-01", description: "محل نگهداری رول‌های پارچه خام و نخی", warehouse_type: "raw_material" },
  { id: "w2", name: "انبار محصولات نهایی حاما", code: "W-02", description: "محل نگهداری پارچه‌های آماده تحویل و سفارشی", warehouse_type: "finished_goods" }
];

export const DEFAULT_STOCK_ITEMS: StockItem[] = [
  { id: "s1", warehouse_id: "w1", product_id: "p1", quantity: 35, min_stock: 10, reorder_point: 15 },
  { id: "s2", warehouse_id: "w1", product_id: "p2", quantity: 80, min_stock: 20, reorder_point: 30 },
  { id: "s3", warehouse_id: "w2", product_id: "p3", quantity: 15, min_stock: 5, reorder_point: 10 }
];

export const DEFAULT_ORDERS: Order[] = [
  {
    id: "o1",
    order_code: "O-501",
    customer_id: "c1",
    status: "registered",
    description: "تحویل فوری برای مزون رضایی",
    created_at: "2026-07-16T10:30:00Z",
    items: [
      { id: "oi1", order_id: "o1", product_id: "p1", quantity: 10, weight: 5, model_name: "مدل اسلیمی", color: "سرمه‌ای" }
    ]
  },
  {
    id: "o2",
    order_code: "O-502",
    customer_id: "c2",
    status: "cutting",
    description: "سفارش عمده مانتو مدارس",
    created_at: "2026-07-17T14:15:00Z",
    items: [
      { id: "oi2", order_id: "o2", product_id: "p2", quantity: 15, weight: 30, model_name: "طرح کلاسیک M2", color: "مشکی" }
    ]
  },
  {
    id: "o3",
    order_code: "O-503",
    customer_id: "c3",
    status: "delivered",
    description: "تسویه کامل نقدی",
    created_at: "2026-07-18T09:00:00Z",
    items: [
      { id: "oi3", order_id: "o3", product_id: "p3", quantity: 5, weight: 10, model_name: "مدل چهارخانه P3", color: "طوسی" }
    ]
  }
];

export const DEFAULT_TRANSACTIONS: StockTransaction[] = [
  {
    id: "t1",
    warehouse_id: "w1",
    product_id: "p1",
    type: "IN",
    quantity: 35,
    unit: "عدد",
    transaction_category: "domestic_purchase",
    supplier_name: "نساجی اصفهان",
    delivery_date: "2026-07-15",
    reference: "رسید انبار ۱۰۲",
    created_at: "2026-07-15T08:00:00Z",
    user: "مدیر سیستم حاما"
  },
  {
    id: "t2",
    warehouse_id: "w1",
    product_id: "p2",
    type: "IN",
    quantity: 80,
    unit: "کیلوگرم",
    transaction_category: "production",
    reference: "سند تولید ۳۰۴",
    created_at: "2026-07-16T11:00:00Z",
    user: "مدیر سیستم حاما"
  },
  {
    id: "t3",
    warehouse_id: "w2",
    product_id: "p3",
    type: "IN",
    quantity: 15,
    unit: "عدد",
    transaction_category: "production",
    reference: "سند تولید ۳۰۵",
    created_at: "2026-07-17T15:30:00Z",
    user: "مدیر سیستم حاما"
  }
];

export function initializeDatabase() {
  if (!localStorage.getItem("erp_initialized")) {
    localStorage.setItem("erp_user", JSON.stringify(DEFAULT_USER));
    localStorage.setItem("erp_customers", JSON.stringify(DEFAULT_CUSTOMERS));
    localStorage.setItem("erp_groups", JSON.stringify(DEFAULT_GROUPS));
    localStorage.setItem("erp_products", JSON.stringify(DEFAULT_PRODUCTS));
    localStorage.setItem("erp_warehouses", JSON.stringify(DEFAULT_WAREHOUSES));
    localStorage.setItem("erp_stock_items", JSON.stringify(DEFAULT_STOCK_ITEMS));
    localStorage.setItem("erp_orders", JSON.stringify(DEFAULT_ORDERS));
    localStorage.setItem("erp_transactions", JSON.stringify(DEFAULT_TRANSACTIONS));
    localStorage.setItem("erp_initialized", "true");
  }
}

export function getFromStorage<T>(key: string, defaultValue: T): T {
  const data = localStorage.getItem(key);
  return data ? JSON.parse(data) : defaultValue;
}

export function saveToStorage<T>(key: string, data: T): void {
  localStorage.setItem(key, JSON.stringify(data));
}
