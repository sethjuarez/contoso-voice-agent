import styles from "./page.module.css";
import Block from "@/components/block";
import { getCategories } from "@/store/products";
import Chat from "@/components/messaging/chat";
import Section from "@/components/section";
import Voice from "@/components/messaging/voice";
import Header from "@/components/header";
import Footer from "@/components/footer";

const Home = async () => {
  const categories = getCategories();

  return (
    <>
      <Header categories={categories} />
      <Block outerClassName={styles.heroContent}>
        <div className={styles.heroTitle}>Contoso Outdoor Company</div>
        <div className={styles.heroText}>
          Embrace Adventure with Contoso Outdoors - Your Ultimate Partner in
          Exploring the Unseen!
        </div>
        <div className={styles.heroSubText}>
          Choose from a variety of products to help you explore the outdoors.
          From camping to hiking, we have you covered with the best gear and the
          best prices.
        </div>
      </Block>
      <>
        {categories.map((category, i) => (
          <Section key={category.slug} index={i} category={category} />
        ))}
      </>
      <Chat options={{ video: true, file: true }} />
      <Voice />
      <Footer />
    </>
  );
};

export default Home;
