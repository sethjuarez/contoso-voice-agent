import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface User {
  name: string;
  email: string;
  image?: string;
}

export interface UserState {
  user: User | null;
  setUser: (name: string, email: string, image?: string) => void;
  resetUser: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      setUser: (name, email, image) =>
        set({ user: { name: name, email: email, image: image } }),
      resetUser: () => set({ user: null }),
    }),
    {
      name: "user-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
