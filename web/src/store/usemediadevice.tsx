import { useEffect, useState } from "react";

export interface MediaDeviceState {
  devices: MediaDeviceInfo[];
  error: string | null;
  isLoading: boolean;
}

export const useMediaDevices = (requestPermission: boolean = false) => {
  const [state, setState] = useState<MediaDeviceState>({
    devices: [],
    error: null,
    isLoading: true,
  });

  useEffect(() => {
    if (
      typeof navigator === "undefined" ||
      typeof navigator.mediaDevices === "undefined"
    ) {
      setState((s) => ({ ...s, error: "Media devices are not available" }));
      return;
    }

    const handleDeviceChange = async () => {
      try {
        if (requestPermission) {
          await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false,
          });
        }

        const mediaDevices = await navigator.mediaDevices.enumerateDevices();
        setState((s) => ({ ...s, devices: mediaDevices, isLoading: false }));
      } catch (err) {
        console.error("Error accessing media devices:", err);
        setState((s) => ({
          ...s,
          error: "Error accessing media devices",
          isloading: false,
        }));
      }
    };
    setState((s) => ({ ...s, isLoading: true }));
    handleDeviceChange();

    navigator.mediaDevices.addEventListener("devicechange", handleDeviceChange);

    return () => {
      navigator.mediaDevices.removeEventListener(
        "devicechange",
        handleDeviceChange
      );
    };
  }, [requestPermission]);

  return state;
};
