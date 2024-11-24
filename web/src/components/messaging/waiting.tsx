import styles from "./waiting.module.css";

const Waiting = () => {
  return (
    <div className={styles.frame}>
      <div className={styles.snippet} data-title="dotpulse">
        <div className={styles.stage}>
          <div className={styles.dotpulse}></div>
        </div>
      </div>
    </div>
  );};

  export default Waiting;