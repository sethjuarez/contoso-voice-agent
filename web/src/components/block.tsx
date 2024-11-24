
import clsx from "clsx";
import { ReactNode } from "react";
import styles from "./block.module.css";

type Props = {
  children: ReactNode;
  outerClassName?: string;
  innerClassName?: string;
};

const Block = ({ children, outerClassName, innerClassName }: Props) => {
  
  return (
    <div className={clsx(outerClassName)}>
      <div className={clsx(styles.innerBlock, innerClassName)}>{children}</div>
    </div>
  );
};

export default Block;
