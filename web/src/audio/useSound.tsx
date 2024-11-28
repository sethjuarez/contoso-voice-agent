import { useEffect, useRef } from "react";


export const useSound = (audioSource: string) => {
  const soundRef = useRef<HTMLAudioElement>();

  useEffect(() => {
    soundRef.current = new Audio(audioSource);
    soundRef.current.loop = true;
  }, [audioSource]);

  const playSound = () => {
    if(soundRef.current === null) return;
    soundRef.current!.play();
  };

  const pauseSound = () => {
    if (soundRef.current === null) return;
    soundRef.current!.pause();
  };

  const stopSound = () => {
    if (soundRef.current === null) return;
    soundRef.current!.pause();
    soundRef.current!.currentTime = 0;
  };

  return {
    playSound,
    pauseSound,
    stopSound,
  };
};
 
 
 
