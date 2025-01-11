"use client";
import Image from "next/image";
import Block from "./block";
import styles from "./header.module.css";
import { getCategories } from "@/store/products";
import { GiHamburgerMenu } from "react-icons/gi";
//import { getServerSession } from "next-auth/next";
//import { authOptions } from "../auth";
import { routes } from "@/data/routes";
import usePersistStore from "@/store/usePersistStore";
import { useUserStore } from "@/store/user";
import { useEffect } from "react";
import { fetchUser } from "@/data/user";
import { BiSolidUserCircle } from "react-icons/bi";

const Header = () => {
  const userState = usePersistStore(useUserStore, (state) => state);
  const user = usePersistStore(useUserStore, (state) => state.user);
  /** Current User */
  useEffect(() => {
    if (!userState?.user) {
      fetchUser().then((u) => {
        userState?.setUser(u.name, u.email, u.image);
      });
    }
  }, [userState, userState?.user]);

  const categories = getCategories();

  const getUserIcon = () => {
    if (user && user.image && user.image !== "undefined") {
      return (
        <Image
          src={user.image}
          width={32}
          height={32}
          alt={user.name}
          className={styles.userIcon}
        />
      );
    }
    return (
      <div className={styles.simpleUser}>
        <BiSolidUserCircle size={38} />
      </div>
    );
  };

  return (
    <Block innerClassName={styles.innerBlock}>
      <div className={styles.baricon}>
        <a title="home" href="/">
          <GiHamburgerMenu size={22} className={styles.username} />
        </a>
      </div>
      <div className={styles.categories}>
        {categories.map((category) => (
          <a href={"#"} key={category.slug} className={styles.category}>
            {category.name}
          </a>
        ))}
        {routes.map((route) => (
          <a href={route.href} key={route.id} className={styles.category}>
            {route.title}
          </a>
        ))}
      </div>
      <div className={styles.grow} />
      <div className={styles.user}>
        <div>
          <div className={styles.username}>{user?.name}</div>
          <div className={styles.email}>{user?.email}</div>
        </div>
        <div className="">
          {getUserIcon()}
        </div>
      </div>
    </Block>
  );
};

export default Header;
