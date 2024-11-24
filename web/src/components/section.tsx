import styles from "./section.module.css";
import { Category } from "@/store/products";
import Block from "./block";
import Image from "next/image";
import clsx from "clsx";

type Props = {
  category: Category;
  index: number;
};
const Section = ({ category, index }: Props) => {
  return (
    <Block
      outerClassName={clsx(
        styles.categoryBlock,
        index % 2 === 0 ? styles.evenSection : styles.oddSection
      )}
    >
      <div
        className={clsx(
          styles.categoryTitle,
          index % 2 === 0 ? styles.evenSection : styles.oddSection
        )}
      >
        {category.name}
      </div>
      <div
        className={clsx(
          styles.categoryDescription,
          index % 2 === 0 ? styles.evenSection : styles.oddSection
        )}
      >
        {category.description}
      </div>
      <div className={styles.productSection}>
        {category.products.map((product) => (
          <div key={product.id} className={styles.itemContainer}>
            <a href="#">
              <Image
                src={product.images[0]}
                width={350}
                height={350}
                alt={product.name}
                className={styles.itemImage}
              />
              <div
                className={clsx(
                  styles.itemName,
                  index % 2 === 0 ? styles.evenSection : styles.oddSection
                )}
              >
                {product.name}
              </div>
            </a>
          </div>
        ))}
      </div>
    </Block>
  );
};

export default Section;
