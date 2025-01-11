import { Turn } from "@/store/chat";
import styles from "./message.module.css";
import { GrUser } from "react-icons/gr";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";
import { fetchCachedImage } from "@/store/images";
import Waiting from "./waiting";
import { HiOutlineSpeakerWave } from "react-icons/hi2";
import { BiSolidUserCircle } from "react-icons/bi";

type Props = {
  turn: Turn;
  notify?: () => void;
};

const getAvatar = (turn: Turn) => {
  if (turn.type === "assistant") {
    return (
      <img
        className={styles.assistantIcon}
        src={"/images/trees.png"}
        alt="Assistant"
      />
    );
  } else if (turn.avatar) {
    if (turn.avatar === "undefined") {
      return (
        <div className={styles.simpleUser}>
          <BiSolidUserCircle size={38} />
        </div>
      );
    } else {
      return (
        <div>
          <img
            src={turn.avatar}
            alt={turn.name}
            className={styles.userIcon}
          />
        </div>
      );
    }
  } else {
    return (
      <div className={styles.assistantIcon}>
        <GrUser size={32} />
      </div>
    );
  }
};

const MessageData = ({ turn, notify }: Props) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  if (turn.image) {
    fetchCachedImage(turn.image, setImageUrl).then(() => {
      if (notify) notify();
    });
  }

  if (turn.type === "assistant") {
    if (turn.status === "waiting")
      return (
        <div className={styles.messageAssistant}>
          <Waiting />
        </div>
      );
    else
      return (
        <div className={styles.messageAssistant}>
          {turn.status === "voice" ? (
            <>
              <HiOutlineSpeakerWave size={24} className={styles.audioIcon} />
              {turn.message}
            </>
          ) : (
            <Markdown remarkPlugins={[remarkGfm]}>{turn.message}</Markdown>
          )}
        </div>
      );
  } else {
    return (
      <div className={styles.messageUser}>
        {imageUrl && (
          <img
            src={imageUrl}
            className={styles.messageImage}
            alt="Current Image"
          />
        )}
        <div>
          {turn.status === "voice" && (
            <HiOutlineSpeakerWave size={24} className={styles.audioIcon} />
          )}
          {turn.message}
        </div>
      </div>
    );
  }
};

const Message = ({ turn, notify }: Props) => {
  return (
    <div
      className={
        turn.type === "user"
          ? styles.messageContainerUser
          : styles.messageContainerAssistant
      }
    >
      <MessageData turn={turn} notify={notify} />
      {getAvatar(turn)}
    </div>
  );
};

export default Message;
