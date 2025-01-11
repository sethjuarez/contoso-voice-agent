"use client";
import Block from "./block";
import styles from "./header.module.css";
import { getCategories } from "@/store/products";
import { GiHamburgerMenu } from "react-icons/gi";
//import { getServerSession } from "next-auth/next";
//import { authOptions } from "../auth";
import { routes } from "@/data/routes";
import usePersistStore from "@/store/usePersistStore";
import { User } from "@/data/user";
import { BiSolidUserCircle } from "react-icons/bi";
import Link from "next/link";

type Props = {
  user: User;
};

const Header = ({ user }: Props) => {

  const categories = getCategories();

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
          <GiHamburgerMenu size={22} className={styles.username} />
        </Link>
      </div>
      <div className={styles.categories}>
        {categories.map((category) => (
          <Link href={"#"} key={category.slug} className={styles.category}>
            {category.name}
          </Link>
        ))}
        {routes.map((route) => (
          <Link href={route.href} key={route.id} className={styles.category}>
            {route.title}
          </Link>
        ))}
      </div>
      <div className={styles.grow} />
      <div className={styles.user}>
        <div>
          <div className={styles.username}>{user.name}</div>
          <div className={styles.email}>{user.email}</div>
        </div>
        <div className="">{getUserIcon()}</div>
      </div>
    </Block>
  );
};

export default Header;
