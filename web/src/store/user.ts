import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface User {
  name: string;
  email: string;
  image?: string;
}

export interface UserState {
  user: User | undefined;
  setUser: (name: string, email: string, image?: string) => void;
  resetUser: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: undefined,
      setUser: (name, email, image) =>
        set({ user: { name: name, email: email, image: image } }),
      resetUser: () => set({ user: undefined }),
    }),
    {
      name: "user-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
