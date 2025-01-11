import Block from "./block";
import styles from "./footer.module.css";
import { getCategories } from "@/store/products";
import Image from "next/image";
import { routes } from "@/data/routes";
import Link from "next/link";

const Footer = async ({
  searchParams,
}: {
  searchParams?: { [key: string]: string | string[] | undefined };
}) => {


  const categories = getCategories();
  
  const legal = ["Site Terms of Use", "Plan Terms & Conditions", "Acceptable Use Policy"];
  const legalLinks = ["#", "#", "#"];

  return (
    <Block
      outerClassName={styles.outerBlock}
      innerClassName={styles.innerBlock}
    >
      <div className={styles.baricon}>
        <Link
          title="home"
          href={`/${searchParams?.type ? "?type=" + searchParams.type : ""}`}
        >
          <Image src="/images/logo.png" alt="logo" width={120} height={120} />
        </Link>
        <div className={styles.company}>Contoso Outdoor Company</div>
      </div>

      <div className={styles.categories}>
        <div>What we do</div>
        <div className={styles.innerCategory}>
          {categories.slice(0, 4).map((category) => (
            <Link href={"#"} key={category.slug} className={styles.category}>
              {category.name}
            </Link>
          ))}
        </div>
      </div>
      <div className={styles.categories}>
        <div>&nbsp;</div>
        <div className={styles.innerCategory}>
          {categories.slice(4, 9).map((category) => (
            <Link
              href={`/category/${category.slug}`}
              key={category.slug}
              className={styles.category}
            >
              {category.name}
            </Link>
          ))}
        </div>
      </div>
      <div className={styles.categories}>
        <div>Need Help?</div>
        <div className={styles.innerCategory}>
          {routes.map((route) => (
            <Link href={route.href} key={route.id} className={styles.category}>
              {route.title}
            </Link>
          ))}
        </div>
      </div>
      <div className={styles.categories}>
        <div>Legal</div>
        <div className={styles.innerCategory}>
          {legal.map((l, i) => (
            <Link href={legalLinks[i]} key={l} className={styles.category}>
              {l.charAt(0).toUpperCase() + l.slice(1)}
            </Link>
          ))}
        </div>
      </div>
      <div className={styles.grow} />
    </Block>
  );
};

export default Footer;
