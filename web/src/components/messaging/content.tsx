import Markdown from "react-markdown";
import styles from "./content.module.css";
import remarkGfm from "remark-gfm";
import { GrPowerReset, GrClose, GrSend, GrTrigger } from "react-icons/gr";
import { SimpleMessage } from "@/socket/types";
import { useState } from "react";
import { startSuggestionTask, suggestionRequested } from "@/socket/action";


const messages: SimpleMessage[] = [
  {
    name: "user",
    text: "I just want to make this trip happen without me freezing to death or, you know, the like. So anything you can give to me or show me.",
  },
  {
    name: "assistant",
    text: "I understand you're gearing up for a snow camping trip and want to stay warm and safe out there. With the image you shared earlier of a tent in snowy conditions, it looks like you're well-prepared with your SkyView 2-Person Tent. Before we dive into product recommendations, is there anything else I should know about your trip?",
  },
  {
    name: "user",
    text: "Oh, what do you got for me?",
  },
  {
    name: "assistant",
    text: "For your snow camping adventure, let's ensure you're fully equipped!\n\n1. **MountainDream Sleeping Bag**: This bag is perfect for cold conditions, keeping you warm even when temperatures drop to 15\u00b0F. It's water-resistant and has a contoured mummy shape for heat retention.\n\n2. **RainGuard Hiking Jacket**: It\u2019s waterproof and breathable, with an adjustable hood and ventilation zippers, keeping you dry and comfortable.\n\n3. **TrekReady Hiking Boots**: These sturdy, insulated boots will provide warmth, support, and excellent traction in snowy conditions.\n\nLet's get you set up for a warm and safe trip! Are there any other items you're interested in?",
  },
  {
    name: "user",
    text: "Before I get too far, I'd love it if you could actually show me and then.",
  },
  {
    name: "assistant",
    text: "Absolutely! I can help you visualize your gear for the trip.",
  },
];

type Props = {
  suggestions?: string[];
  debug?: boolean;
  onClose: () => void;
};

const Content = ({ suggestions, debug, onClose }: Props) => {
  const [content, setContent] = useState<string[]>(
    suggestions ? suggestions : []
  );

  const clear = () => {
    setContent([]);
  };

  const close = () => {
    onClose();
  };

  const createSuggestions = async () => {
    setContent([]);
    const task = await startSuggestionTask(messages);
    for await (const chunk of task) {
      setContent((prev) => [...prev, chunk]);
    }
  };

  const testWriteUp = async () => {
    const response = await suggestionRequested(messages);
    console.log("testWriteUp", messages, response);
  };

  return (
    <div className={styles.contentWindow}>
      <div className={styles.contentTitle}>
        <div className={"grow"} />
        {debug && (
          <>
            <GrTrigger
              size={18}
              className={styles.contentIcon}
              onClick={testWriteUp}
            />
            <GrSend
              size={18}
              className={styles.contentIcon}
              onClick={createSuggestions}
            />
            <GrPowerReset
              size={18}
              className={styles.contentIcon}
              onClick={clear}
            />{" "}
          </>
        )}
        <GrClose size={18} className={styles.contentIcon} onClick={close} />
      </div>
      <Markdown className={styles.content} remarkPlugins={[remarkGfm]}>
        {content.join("")}
      </Markdown>
    </div>
  );
};

export default Content;
