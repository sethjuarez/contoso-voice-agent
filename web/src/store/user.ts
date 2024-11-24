import { create } from "zustand";

export interface User {
  name: string;
  email: string;
  image: string;
}

export interface UserState {
  user: User | null;
  setUser: (name: string, email: string, user: string) => void;
}

export const useUserStore = create<UserState>()((set) => ({
  user: null,
  setUser: (name, email, image) =>
    set({ user: { name: name, email: email, image: image } }),
}));

