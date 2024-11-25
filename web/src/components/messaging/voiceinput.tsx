import { FormEvent, useEffect, useState } from "react";
import styles from "./voiceinput.module.css";



const VoiceInput = () => {
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<MediaDeviceInfo>();

  const getDevices = async (): Promise<MediaDeviceInfo[] | null> => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter((device) => device.kind === "audioinput");
    } catch (err) {
      if (err instanceof DOMException) {
        if (
          err.name == "NotAllowedError" ||
          err.name == "PermissionDeniedError"
        )
          alert("Please allow camera access to use this feature.");
      } else {
        alert("Error accessing camera.");
        console.error(err);
      }
      return null;
    }
  };

  

  useEffect(() => {
    const getSelectedDevice = async (): Promise<MediaDeviceInfo | null> => {
      const devices = await getDevices();
      if (!devices) return null;
      setDevices(devices);

      const device = localStorage.getItem("selected-audio-device");

      if (device) {
        const parsedDevice = JSON.parse(device);
        const dvc = devices?.find((d) => d.deviceId === parsedDevice.deviceId);
        if (dvc) {
          return dvc;
        } else {
          // remove selected device if not found (bad entry)
          localStorage.removeItem("selected-audio-device");
          return devices?.[0];
        }
      } else {
        return devices?.[0];
      }
    };
    
    getSelectedDevice().then((device) => 
      setSelectedDevice(device ?? devices[0]));
  }, [devices]);
  

  useEffect(() => {
    if (selectedDevice) {
      localStorage.setItem(
        "selected-audio-device",
        JSON.stringify({ deviceId: selectedDevice.deviceId })
      );
    }
  }, [selectedDevice]);

  return (
    <select
      id="device"
      name="device"
      className={styles.mediaselect}
      value={selectedDevice?.deviceId}
      title="Select a device"
      onInput={(e: FormEvent<HTMLSelectElement>) =>
        setSelectedDevice(
          devices.find((d) => d.deviceId === e.currentTarget.value)
        )
      }
    >
      {devices.map((device) => {
        return (
          <option key={device.deviceId} value={device.deviceId}>
            {device.label}
          </option>
        );
      })}
    </select>
  );
};

export default VoiceInput;
