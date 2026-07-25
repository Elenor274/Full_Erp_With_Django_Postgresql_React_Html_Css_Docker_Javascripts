export interface Customer {
  id: string;
  customer_code: string;
  name: string;
  last_name: string;
  phone_number: string;
}

export interface ProductGroup {
  id: string;
  name: string;
}

export interface Product {
  id: string;
  code: string;
  group_id: string;
  name: string;
  unit: "عدد" | "کیلوگرم" | "بسته";
  initial_stock: number;
  unit_price: number;
  description?: string;
}

export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  quantity: number;
  weight: number; // in KG
  model_name?: string;
  color?: string;
}

export interface Order {
  id: string;
  order_code: string;
  customer_id: string;
  status: "registered" | "cutting" | "sewing" | "quality" | "warehouse" | "delivered" | "cancelled";
  description?: string;
  created_at: string;
  items: OrderItem[];
}

export interface Warehouse {
  id: string;
  name: string;
  code: string;
  description?: string;
  warehouse_type: "raw_material" | "finished_goods" | "semi_finished" | "other";
}

export interface StockItem {
  id: string;
  warehouse_id: string;
  product_id: string;
  quantity: number;
  min_stock: number;
  max_stock?: number;
  reorder_point: number;
}

export interface StockTransaction {
  id: string;
  warehouse_id: string;
  product_id: string;
  type: "IN" | "OUT";
  quantity: number;
  unit: string;
  supplier_name?: string;
  delivery_date?: string;
  consumption_amount?: number;
  transaction_category: "foreign_purchase" | "domestic_purchase" | "production" | "return" | "other";
  reference?: string;
  created_at: string;
  user: string;
}

export interface User {
  username: string;
  full_name: string;
  email: string;
}
