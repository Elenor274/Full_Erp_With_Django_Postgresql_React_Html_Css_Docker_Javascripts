import React, { useState, useEffect } from "react";
import { Order, Customer, Product, OrderItem } from "../types";
import { Plus, Search, Eye, Trash2, Edit, X, ShoppingBag, PlusCircle, Trash } from "lucide-react";
import { motion } from "motion/react";

interface OrdersProps {
  orders: Order[];
  setOrders: (orders: Order[]) => void;
  customers: Customer[];
  products: Product[];
  selectedOrderId: string | null;
  setSelectedOrderId: (id: string | null) => void;
  initialTab?: string;
}

export default function Orders({
  orders,
  setOrders,
  customers,
  products,
  selectedOrderId,
  setSelectedOrderId,
  initialTab,
}: OrdersProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  
  // Create / Edit Form State
  const [isFormOpen, setIsFormOpen] = useState(initialTab === "create");
  const [editingOrder, setEditingOrder] = useState<Order | null>(null);
  
  const [orderFormData, setOrderFormData] = useState({
    order_code: "",
    customer_id: "",
    status: "registered" as Order["status"],
    description: "",
  });
  
  // Dynamic order items list
  const [orderItemsData, setOrderItemsData] = useState<Array<{
    product_id: string;
    quantity: number;
    weight: number;
    model_name: string;
    color: string;
  }>>([{ product_id: "", quantity: 1, weight: 0, model_name: "", color: "" }]);

  // Detail view state
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  useEffect(() => {
    if (selectedOrderId) {
      setIsDetailOpen(true);
    }
  }, [selectedOrderId]);

  // Open Create Form
  const openCreateForm = () => {
    const lastCodeNum = orders.reduce((max, o) => {
      const match = o.order_code.match(/O-(\d+)/);
      if (match) {
        const num = parseInt(match[1]);
        return num > max ? num : max;
      }
      return max;
    }, 500);

    setOrderFormData({
      order_code: `O-${lastCodeNum + 1}`,
      customer_id: customers[0]?.id || "",
      status: "registered",
      description: "",
    });
    setOrderItemsData([{ product_id: products[0]?.id || "", quantity: 1, weight: 1, model_name: "", color: "" }]);
    setEditingOrder(null);
    setIsFormOpen(true);
  };

  // Add order item row
  const addItemRow = () => {
    setOrderItemsData([
      ...orderItemsData,
      { product_id: products[0]?.id || "", quantity: 1, weight: 1, model_name: "", color: "" }
    ]);
  };

  // Remove order item row
  const removeItemRow = (idx: number) => {
    if (orderItemsData.length === 1) return;
    setOrderItemsData(orderItemsData.filter((_, i) => i !== idx));
  };

  // Change item row values
  const handleItemRowChange = (idx: number, field: string, value: any) => {
    const updated = orderItemsData.map((item, i) => {
      if (i === idx) {
        return { ...item, [field]: value };
      }
      return item;
    });
    setOrderItemsData(updated);
  };

  // Submit Order (Create)
  const handleOrderSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderFormData.order_code || !orderFormData.customer_id) {
      alert("لطفاً فیلدهای الزامی را تکمیل کنید.");
      return;
    }

    // Validate items
    const invalidItem = orderItemsData.some(item => !item.product_id || item.quantity <= 0);
    if (invalidItem) {
      alert("لطفاً اطلاعات کالاها را با مقادیر صحیح وارد نمایید.");
      return;
    }

    const orderId = editingOrder ? editingOrder.id : `o_${Date.now()}`;

    // Map rows to OrderItem types
    const mappedItems: OrderItem[] = orderItemsData.map((item, index) => ({
      id: `${orderId}_item_${index}`,
      order_id: orderId,
      product_id: item.product_id,
      quantity: Number(item.quantity),
      weight: Number(item.weight),
      model_name: item.model_name,
      color: item.color
    }));

    if (editingOrder) {
      // Edit
      const updated = orders.map(o =>
        o.id === editingOrder.id ? { ...o, ...orderFormData, items: mappedItems } : o
      );
      setOrders(updated);
    } else {
      // Create
      if (orders.some(o => o.order_code === orderFormData.order_code)) {
        alert("کد سفارش تکراری است.");
        return;
      }

      const newOrder: Order = {
        id: orderId,
        order_code: orderFormData.order_code,
        customer_id: orderFormData.customer_id,
        status: orderFormData.status,
        description: orderFormData.description,
        created_at: new Date().toISOString(),
        items: mappedItems
      };
      setOrders([newOrder, ...orders]);
    }

    setIsFormOpen(false);
  };

  // Delete Order
  const handleDeleteOrder = (id: string) => {
    if (confirm("آیا از حذف این سفارش اطمینان دارید؟")) {
      setOrders(orders.filter(o => o.id !== id));
      if (selectedOrderId === id) {
        setSelectedOrderId(null);
        setIsDetailOpen(false);
      }
    }
  };

  // Status mapping
  const statusLabels: Record<Order["status"], { text: string; bg: string; textCol: string }> = {
    registered: { text: "ثبت شده", bg: "bg-blue-50", textCol: "text-blue-600" },
    cutting: { text: "برش", bg: "bg-amber-50", textCol: "text-amber-600" },
    sewing: { text: "دوخت", bg: "bg-purple-50", textCol: "text-purple-600" },
    quality: { text: "کنترل کیفیت", bg: "bg-indigo-50", textCol: "text-indigo-600" },
    warehouse: { text: "انبار", bg: "bg-sky-50", textCol: "text-sky-600" },
    delivered: { text: "تحویل داده شد", bg: "bg-emerald-50", textCol: "text-emerald-600" },
    cancelled: { text: "لغو شده", bg: "bg-rose-50", textCol: "text-rose-600" },
  };

  const getCustomerName = (id: string) => {
    const cust = customers.find(c => c.id === id);
    return cust ? `${cust.name} ${cust.last_name}` : "—";
  };

  const calculateOrderTotal = (order: Order) => {
    return order.items.reduce((sum, item) => {
      const prod = products.find(p => p.id === item.product_id);
      const price = prod ? prod.unit_price : 0;
      return sum + item.quantity * price;
    }, 0);
  };

  const getProductDetail = (prodId: string) => {
    return products.find(p => p.id === prodId);
  };

  // Filter orders
  const filteredOrders = orders.filter(o => {
    const query = searchQuery.toLowerCase();
    const matchesQuery =
      o.order_code.toLowerCase().includes(query) ||
      getCustomerName(o.customer_id).toLowerCase().includes(query) ||
      (o.description && o.description.toLowerCase().includes(query));
    
    const matchesStatus = statusFilter === "all" || o.status === statusFilter;

    return matchesQuery && matchesStatus;
  });

  const selectedOrder = orders.find(o => o.id === selectedOrderId);

  return (
    <div className="space-y-6">
      {/* Header Panel */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">مدیریت سفارشات حاما</h1>
          <p className="text-xs text-slate-500 font-medium mt-1">مدیریت فاکتورها، روند تولید (برش، دوخت) و خروجی فاکتورها</p>
        </div>
        <button
          onClick={openCreateForm}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white rounded-lg text-xs font-bold shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>ثبت سفارش جدید</span>
        </button>
      </div>

      {/* Main Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left List Columns */}
        <div className={`bg-white border border-slate-100 rounded-xl p-5 shadow-sm space-y-4 ${selectedOrderId ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
          {/* Controls */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute right-3 top-2.5" />
              <input
                type="text"
                placeholder="جستجوی کد سفارش، مشتری، توضیحات..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full text-xs font-semibold pr-9 pl-3 py-2 border border-slate-100 rounded-lg bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/15 focus:border-brand-500 transition-all"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs font-semibold px-3 py-2 border border-slate-100 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/15"
            >
              <option value="all">همه وضعیت‌ها</option>
              <option value="registered">ثبت شده</option>
              <option value="cutting">برش</option>
              <option value="sewing">دوخت</option>
              <option value="quality">کنترل کیفیت</option>
              <option value="warehouse">انبار</option>
              <option value="delivered">تحویل داده شد</option>
              <option value="cancelled">لغو شده</option>
            </select>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            {filteredOrders.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-400">هیچ سفارشی یافت نشد.</div>
            ) : (
              <table className="w-full text-right text-xs">
                <thead>
                  <tr className="text-slate-400 font-bold border-b border-slate-100">
                    <th className="py-3 px-2">کد سفارش</th>
                    <th className="py-3 px-2">مشتری</th>
                    <th className="py-3 px-2">تاریخ ثبت</th>
                    <th className="py-3 px-2">مبلغ کل (ریال)</th>
                    <th className="py-3 px-2 text-center">وضعیت</th>
                    <th className="py-3 px-2 text-left">عملیات</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {filteredOrders.map((o) => {
                    const status = statusLabels[o.status] || { text: o.status, bg: "bg-slate-50", textCol: "text-slate-600" };
                    return (
                      <tr
                        key={o.id}
                        className={`text-slate-700 hover:bg-slate-50/50 transition-colors cursor-pointer ${
                          selectedOrderId === o.id ? "bg-brand-50/40 border-l-2 border-brand-500" : ""
                        }`}
                        onClick={() => setSelectedOrderId(o.id)}
                      >
                        <td className="py-3 px-2 font-bold text-slate-800">{o.order_code}</td>
                        <td className="py-3 px-2 font-semibold text-slate-900">{getCustomerName(o.customer_id)}</td>
                        <td className="py-3 px-2 font-mono text-slate-400">
                          {new Date(o.created_at).toLocaleDateString("fa-IR")}
                        </td>
                        <td className="py-3 px-2 font-mono font-bold text-slate-800">
                          {calculateOrderTotal(o).toLocaleString()}
                        </td>
                        <td className="py-3 px-2 text-center">
                          <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${status.bg} ${status.textCol}`}>
                            {status.text}
                          </span>
                        </td>
                        <td className="py-3 px-2 text-left" onClick={(e) => e.stopPropagation()}>
                          <div className="inline-flex gap-2">
                            <button
                              onClick={() => setSelectedOrderId(o.id)}
                              className="p-1 text-slate-400 hover:text-brand-500 hover:bg-slate-50 rounded"
                              title="مشاهده جزئیات"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteOrder(o.id)}
                              className="p-1 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded"
                              title="حذف سفارش"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Right Detail Panel (If opened) */}
        {selectedOrderId && selectedOrder && isDetailOpen && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white border border-slate-100 rounded-xl p-5 shadow-lg flex flex-col space-y-4"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-50">
              <div className="flex items-center gap-2">
                <ShoppingBag className="w-4.5 h-4.5 text-brand-500" />
                <h2 className="text-sm font-extrabold text-slate-800">سفارش {selectedOrder.order_code}</h2>
              </div>
              <button
                onClick={() => {
                  setSelectedOrderId(null);
                  setIsDetailOpen(false);
                }}
                className="p-1 text-slate-400 hover:bg-slate-50 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Details Content */}
            <div className="space-y-4 text-xs font-semibold">
              <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50/50 rounded-xl border border-slate-100/50">
                <div>
                  <div className="text-[10px] text-slate-400 font-bold mb-0.5">مشتری</div>
                  <div className="text-slate-800">{getCustomerName(selectedOrder.customer_id)}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 font-bold mb-0.5">تاریخ ثبت</div>
                  <div className="text-slate-800 font-mono">
                    {new Date(selectedOrder.created_at).toLocaleString("fa-IR")}
                  </div>
                </div>
              </div>

              {/* Status Update Dropdown */}
              <div>
                <label className="block text-[10px] text-slate-400 font-bold mb-1.5">تغییر وضعیت سفارش</label>
                <select
                  value={selectedOrder.status}
                  onChange={(e) => {
                    const status = e.target.value as Order["status"];
                    setOrders(
                      orders.map(o => (o.id === selectedOrder.id ? { ...o, status } : o))
                    );
                  }}
                  className="w-full px-3 py-2 border border-slate-100 rounded-lg bg-white focus:outline-none text-xs font-bold"
                >
                  <option value="registered">ثبت شده</option>
                  <option value="cutting">برش</option>
                  <option value="sewing">دوخت</option>
                  <option value="quality">کنترل کیفیت</option>
                  <option value="warehouse">انبار</option>
                  <option value="delivered">تحویل داده شد</option>
                  <option value="cancelled">لغو شده</option>
                </select>
              </div>

              {/* Description */}
              {selectedOrder.description && (
                <div>
                  <div className="text-[10px] text-slate-400 font-bold mb-1">توضیحات</div>
                  <div className="p-2.5 bg-slate-50 rounded-lg text-slate-600 leading-relaxed font-normal text-[11px]">
                    {selectedOrder.description}
                  </div>
                </div>
              )}

              {/* Order Items Table */}
              <div>
                <div className="text-[10px] text-slate-400 font-bold mb-2">لیست اقلام سفارش</div>
                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {selectedOrder.items.map((item, idx) => {
                    const prod = getProductDetail(item.product_id);
                    return (
                      <div key={idx} className="p-3 bg-white border border-slate-100 rounded-xl space-y-1 shadow-sm">
                        <div className="flex justify-between items-center">
                          <span className="font-bold text-slate-800 text-xs">{prod ? prod.name : "کالای نامشخص"}</span>
                          <span className="font-mono text-[10px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                            {item.quantity} {prod?.unit || "واحد"}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-1.5 text-[10px] text-slate-400 font-medium">
                          <span>وزن: {item.weight}kg</span>
                          <span>مدل: {item.model_name || "—"}</span>
                          <span>رنگ: {item.color || "—"}</span>
                        </div>
                        {prod && (
                          <div className="flex justify-between items-center text-[10px] font-bold text-slate-500 pt-1 border-t border-slate-50">
                            <span>قیمت کالا: {prod.unit_price.toLocaleString()}</span>
                            <span className="text-brand-500 font-mono font-bold">
                              {(item.quantity * prod.unit_price).toLocaleString()} ریال
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Big total */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-slate-400 font-bold">مبلغ نهایی سفارش:</span>
                <span className="font-mono font-extrabold text-sm text-brand-500">
                  {calculateOrderTotal(selectedOrder).toLocaleString()} ریال
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Full screen / Big Form Modal for Order Creation / Editing */}
      {isFormOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-[9999] overflow-y-auto">
          <div className="bg-white border border-slate-100 rounded-xl w-full max-w-3xl p-6 shadow-2xl relative my-8">
            <button
              onClick={() => setIsFormOpen(false)}
              className="absolute top-4 left-4 p-1.5 text-slate-400 hover:bg-slate-50 rounded-lg"
            >
              <X className="w-4.5 h-4.5" />
            </button>

            <h2 className="text-sm font-extrabold text-slate-800 pb-3 border-b border-slate-50">
              ثبت سفارش جدید حاما
            </h2>

            <form onSubmit={handleOrderSubmit} className="space-y-6 mt-4 text-xs font-semibold">
              {/* Order Metadata */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-slate-400 mb-1.5 font-bold">کد سفارش <span className="text-rose-500">*</span></label>
                  <input
                    type="text"
                    required
                    value={orderFormData.order_code}
                    onChange={(e) => setOrderFormData({ ...orderFormData, order_code: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/10 focus:border-brand-500 transition-all font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1.5 font-bold">انتخاب مشتری <span className="text-rose-500">*</span></label>
                  <select
                    required
                    value={orderFormData.customer_id}
                    onChange={(e) => setOrderFormData({ ...orderFormData, customer_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-100 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/10 focus:border-brand-500 transition-all"
                  >
                    <option value="">-- انتخاب مشتری --</option>
                    {customers.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.name} {c.last_name} ({c.customer_code})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1.5 font-bold">وضعیت اولیه <span className="text-rose-500">*</span></label>
                  <select
                    required
                    value={orderFormData.status}
                    onChange={(e) => setOrderFormData({ ...orderFormData, status: e.target.value as Order["status"] })}
                    className="w-full px-3 py-2 border border-slate-100 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/10 focus:border-brand-500 transition-all"
                  >
                    <option value="registered">ثبت شده</option>
                    <option value="cutting">برش</option>
                    <option value="sewing">دوخت</option>
                    <option value="quality">کنترل کیفیت</option>
                    <option value="warehouse">انبار</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1.5 font-bold">توضیحات سفارش</label>
                <textarea
                  rows={2}
                  placeholder="جزئیات دوخت، پارچه، موعد تحویل یا شرایط پرداخت..."
                  value={orderFormData.description}
                  onChange={(e) => setOrderFormData({ ...orderFormData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/10 focus:border-brand-500 transition-all"
                />
              </div>

              {/* Order Items Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-50">
                  <h3 className="text-xs font-extrabold text-slate-700">اقلام و ابعاد پارچه‌ها</h3>
                  <button
                    type="button"
                    onClick={addItemRow}
                    className="flex items-center gap-1.5 px-3 py-1 bg-brand-50 hover:bg-brand-100 text-brand-500 rounded-md text-[10px] font-extrabold transition-colors"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>افزودن ردیف جدید</span>
                  </button>
                </div>

                {/* Items loop */}
                <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                  {orderItemsData.map((item, idx) => {
                    const prod = getProductDetail(item.product_id);
                    return (
                      <div key={idx} className="grid grid-cols-1 md:grid-cols-12 gap-3 p-4 bg-slate-50/50 rounded-xl border border-slate-100/50 items-end">
                        
                        <div className="md:col-span-4">
                          <label className="block text-slate-400 mb-1 text-[10px] font-bold">انتخاب کالا <span className="text-rose-500">*</span></label>
                          <select
                            required
                            value={item.product_id}
                            onChange={(e) => handleItemRowChange(idx, "product_id", e.target.value)}
                            className="w-full px-2 py-1.5 border border-slate-100 rounded-lg bg-white focus:outline-none text-[11px] font-bold"
                          >
                            <option value="">-- انتخاب کالا --</option>
                            {products.map(p => (
                              <option key={p.id} value={p.id}>
                                {p.name} ({p.code})
                              </option>
                            ))}
                          </select>
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-slate-400 mb-1 text-[10px] font-bold">تعداد ({prod?.unit || "واحد"})</label>
                          <input
                            type="number"
                            required
                            min={1}
                            value={item.quantity}
                            onChange={(e) => handleItemRowChange(idx, "quantity", parseInt(e.target.value) || 0)}
                            className="w-full px-2 py-1.5 border border-slate-100 rounded-lg focus:outline-none text-[11px] font-mono"
                          />
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-slate-400 mb-1 text-[10px] font-bold">وزن (KG)</label>
                          <input
                            type="number"
                            required
                            step="0.01"
                            min={0}
                            value={item.weight}
                            onChange={(e) => handleItemRowChange(idx, "weight", parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1.5 border border-slate-100 rounded-lg focus:outline-none text-[11px] font-mono"
                          />
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-slate-400 mb-1 text-[10px] font-bold">مدل</label>
                          <input
                            type="text"
                            placeholder="مثال: M-101"
                            value={item.model_name}
                            onChange={(e) => handleItemRowChange(idx, "model_name", e.target.value)}
                            className="w-full px-2 py-1.5 border border-slate-100 rounded-lg focus:outline-none text-[11px]"
                          />
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-slate-400 mb-1 text-[10px] font-bold">رنگ</label>
                          <input
                            type="text"
                            placeholder="مثال: سرمه‌ای"
                            value={item.color}
                            onChange={(e) => handleItemRowChange(idx, "color", e.target.value)}
                            className="w-full px-2 py-1.5 border border-slate-100 rounded-lg focus:outline-none text-[11px]"
                          />
                        </div>

                        <div className="md:col-span-1 flex justify-center pb-0.5">
                          <button
                            type="button"
                            disabled={orderItemsData.length === 1}
                            onClick={() => removeItemRow(idx)}
                            className="p-1.5 text-slate-400 hover:text-rose-500 disabled:opacity-30 rounded-lg hover:bg-rose-50 transition-colors"
                          >
                            <Trash className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Dynamic total calculation for form */}
              <div className="p-4 bg-brand-50/20 border border-brand-100/50 rounded-xl flex justify-between items-center">
                <span className="text-slate-500 font-bold">مجموع مبالغ اقلام فرم:</span>
                <span className="font-mono font-extrabold text-sm text-brand-600">
                  {orderItemsData.reduce((sum, item) => {
                    const prod = getProductDetail(item.product_id);
                    return sum + (item.quantity * (prod?.unit_price || 0));
                  }, 0).toLocaleString()} ریال
                </span>
              </div>

              {/* Buttons */}
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-50">
                <button
                  type="button"
                  onClick={() => setIsFormOpen(false)}
                  className="px-4 py-2 border border-slate-100 rounded-lg text-slate-500 hover:bg-slate-50 transition-colors"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white rounded-lg shadow-sm"
                >
                  ثبت نهایی سفارش
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
