import Image from "next/image";
import Block from "./block";
import styles from "./header.module.css";
import { getCategories } from "@/store/products";
import { GiHamburgerMenu } from "react-icons/gi";
//import { getServerSession } from "next-auth/next";
//import { authOptions } from "../auth";
import { routes } from "@/data/routes";

const Header = async ({
  searchParams,
}: {
  searchParams?: { [key: string]: string | string[] | undefined };
}) => {
  // TODO: Move to EasyAuth
  /*
  const session = await getServerSession(authOptions);
  
  const user = {
    name: session?.user?.name || "Seth Juarez",
    email: session?.user?.email || "sethjuarez@example.com",
    image: session?.user?.image || "/people/sethjuarez.jpg",
  };
  */

  const user = {
    name: "Seth Juarez",
    email: "sethjuarez@example.com",
    image: "/people/sethjuarez.jpg",
  };

  const categories = getCategories();

  return (
    <Block innerClassName={styles.innerBlock}>
      <div className={styles.baricon}>
        <a
          title="home"
          href={`/${searchParams?.type ? "?type=" + searchParams.type : ""}`}
        >
          <GiHamburgerMenu size={22} className={styles.username} />
        </a>
      </div>
      <div className={styles.categories}>
        {categories.map((category) => (
          <a
            href={"#"}
            key={category.slug}
            className={styles.category}
          >
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
          <div className={styles.username}>{user.name}</div>
          <div className={styles.email}>{user.email}</div>
        </div>
        <div className="">
          <Image
            src={user.image}
            width={32}
            height={32}
            alt={user.name}
            className={styles.userIcon}
          />
        </div>
      </div>
    </Block>
  );
};

export default Header;
