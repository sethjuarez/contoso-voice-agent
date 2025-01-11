import styles from "./page.module.css";
import Block from "../components/block";
import { getCategories } from "../store/products";
import Chat from "@/components/messaging/chat";
import Section from "@/components/section";
import Voice from "@/components/messaging/voice";
import { fetchUser } from "@/data/user";

const Home = async () => {
  const categories = getCategories();
  const user = await fetchUser();

  return (
    <>
      <Block outerClassName={styles.heroContent}>
        <div className={styles.heroTitle}>Contoso Outdoor Company</div>
        <div className={styles.heroText}>
          Embrace Adventure with Contoso Outdoors - Your Ultimate Partner in
          Exploring the Unseen!
        </div>
        <div className={styles.heroSubText}>
          Choose from a variety of products to help you explore the outdoors.
          From camping to hiking, we have you covered with the best gear and the
          best prices. {user.name}
        </div>
      </Block>
      <>
        {categories.map((category, i) => (
          <Section key={category.slug} index={i} category={category} />
        ))}
      </>
      <Chat options={{ video: true, file: true }} />
      <Voice />
    </>
  );
};

export default Home;
