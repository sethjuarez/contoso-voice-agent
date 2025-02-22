"use client";
import Block from "./block";
import Image from "next/image";
import styles from "./header.module.css";
import { useUserStore } from "@/store/user";
import { BiSolidUserCircle } from "react-icons/bi";
import Link from "next/link";
import usePersistStore from "@/store/usePersistStore";
import { useEffect } from "react";
import { fetchUser } from "@/data/user";

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

  const getUserIcon = () => {
    if (user && user.image && user.image !== "undefined") {
      return (
        <img src={user.image} alt={user.name} className={styles.userIcon} />
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
        <Link title="home" href="/">
          <Image
            src={"/images/full-logo.png"}
            alt="logo"
            height={38}
            width={274}
            className={styles.username}
          />
        </Link>
      </div>
      <div className={styles.grow} />
      <div className={styles.user}>
        <div>
          <div className={styles.username}>{user?.name}</div>
          <div className={styles.email}>{user?.email}</div>
        </div>
        <div className="">{getUserIcon()}</div>
      </div>
    </Block>
  );
};

export default Header;
