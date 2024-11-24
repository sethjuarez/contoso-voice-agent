import Block from "./block";
import styles from "./footer.module.css";
import { getCategories } from "@/store/products";
import Image from "next/image";
import { routes } from "@/data/routes";

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
        <a
          title="home"
          href={`/${searchParams?.type ? "?type=" + searchParams.type : ""}`}
        >
          <Image src="/images/logo.png" alt="logo" width={120} height={120} />
        </a>
        <div className={styles.company}>Contoso Outdoor Company</div>
      </div>

      <div className={styles.categories}>
        <div>What we do</div>
        <div className={styles.innerCategory}>
          {categories.slice(0, 4).map((category) => (
            <a
              href={"#"}
              key={category.slug}
              className={styles.category}
            >
              {category.name}
            </a>
          ))}
        </div>
      </div>
      <div className={styles.categories}>
        <div>&nbsp;</div>
        <div className={styles.innerCategory}>
          {categories.slice(4, 9).map((category) => (
            <a
              href={`/category/${category.slug}`}
              key={category.slug}
              className={styles.category}
            >
              {category.name}
            </a>
          ))}
        </div>
      </div>
      <div className={styles.categories}>
        <div>Need Help?</div>
        <div className={styles.innerCategory}>
          {routes.map((route) => (
            <a href={route.href} key={route.id} className={styles.category}>
              {route.title}
            </a>
          ))}
        </div>
      </div>
      <div className={styles.categories}>
        <div>Legal</div>
        <div className={styles.innerCategory}>
          {legal.map((l, i) => (
            <a href={legalLinks[i]} key={l} className={styles.category}>
              {l.charAt(0).toUpperCase() + l.slice(1)}
            </a>
          ))}
        </div>
      </div>
      <div className={styles.grow} />
    </Block>
  );
};

export default Footer;
