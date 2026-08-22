# Cart Context Pattern

A React Context + localStorage pattern for persistent cart state across Next.js pages.

## Provider Structure

```tsx
"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { Produto, ItemCarrinho } from "@/types";

interface CartContextType {
  items: ItemCarrinho[];
  total: number;
  totalItens: number;
  addToCart: (produto: Produto) => void;
  removeFromCart: (item: ItemCarrinho) => void;
  updateQuantidade: (produtoId: number, quantidade: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);
const STORAGE_KEY = "carcrew-cart";

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ItemCarrinho[]>([]);

  // Hydrate on mount (client-side only)
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) setItems(parsed);
      }
    } catch { /* corrupted data */ }
  }, []);

  // Sync to localStorage on change
  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(items)); }
    catch { /* storage unavailable */ }
  }, [items]);

  const addToCart = useCallback((produto: Produto) => {
    setItems((prev) => {
      const existing = prev.find((item) => item.produto.id === produto.id);
      if (existing) {
        return prev.map((item) =>
          item.produto.id === produto.id
            ? { ...item, quantidade: item.quantidade + 1 }
            : item
        );
      }
      return [...prev, { produto, quantidade: 1 }];
    });
  }, []);

  const removeFromCart = useCallback((item: ItemCarrinho) => {
    setItems((prev) => {
      const existing = prev.find((i) => i.produto.id === item.produto.id);
      if (existing && existing.quantidade <= 1) {
        return prev.filter((i) => i.produto.id !== item.produto.id);
      }
      return prev.map((i) =>
        i.produto.id === item.produto.id
          ? { ...i, quantidade: i.quantidade - 1 }
          : i
      );
    });
  }, []);

  const clearCart = useCallback(() => setItems([]), []);

  const total = items.reduce((sum, i) => sum + i.produto.preco * i.quantidade, 0);
  const totalItens = items.reduce((sum, i) => sum + i.quantidade, 0);

  return (
    <CartContext.Provider value={{ items, total, totalItens, addToCart, removeFromCart, updateQuantidade, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) throw new Error("useCart must be used within a CartProvider");
  return context;
}
```

## Key Requirements

1. **Always render the Provider** — Do NOT block children during hydration. The provider must always wrap children, even before useEffect fires. Otherwise SSG/SSR will crash with "useCart must be used within a CartProvider".

2. **Wrap in layout.tsx** — Place inside MuiThemeProvider:
   ```tsx
   <MuiProvider><CartProvider>{children}</CartProvider></MuiProvider>
   ```

3. **CartDrawer receives items + total as props** from the page (via `useCart()`), not from its own context call. This keeps the drawer reusable.

4. **Update Header badge** — Pass `totalItens` from `useCart()` to Header as `cartItemCount` prop.
