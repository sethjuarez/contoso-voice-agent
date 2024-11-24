import { FormEvent, useEffect, useRef, useState } from "react";
import { HiOutlineVideoCamera } from "react-icons/hi2";
import styles from "./videoimagepicker.module.css";
import { GrClose } from "react-icons/gr";
import { readAndCacheVideoFrame } from "@/store/images";

type Props = {
  setCurrentImage: (image: string) => void;
};

const VideoImagePicker = ({ setCurrentImage }: Props) => {
  const [show, setShow] = useState(false);
  const [showCamera, setShowCamera] = useState<boolean>(false);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<MediaDeviceInfo>();
  const videoRef = useRef<HTMLVideoElement>(null);

  const getDevices = async (): Promise<MediaDeviceInfo[] | null> => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter((device) => device.kind === "videoinput");
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

  const getSelectedDevice = async (): Promise<MediaDeviceInfo | null> => {
    const devices = await getDevices();
    if (!devices) return null;

    const device = localStorage.getItem("selected-device");

    if (device) {
      const parsedDevice = JSON.parse(device);
      const dvc = devices?.find((d) => d.deviceId === parsedDevice.deviceId);
      if (dvc) {
        return dvc;
      } else {
        // remove selected device if not found (bad entry)
        localStorage.removeItem("selected-device");
        return devices?.[0];
      }
    } else {
      return devices?.[0];
    }
  };

  const startVideo = async (deviceId: string) => {
    if (videoRef.current) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { deviceId: { exact: deviceId } },
        });
        videoRef.current.disablePictureInPicture = true;
        videoRef.current.srcObject = stream;
        setShowCamera(true);
      } catch (err) {
        alert("Error accessing camera.");
        videoRef.current.srcObject = null;
        setShowCamera(false);
      }
    }
  };

  const showVideo = async () => {
    const devices = await getDevices();
    if (!devices) {
      setShow(false);
      return;
    }

    const device = await getSelectedDevice();
    if (!device) {
      setShow(false);
      return;
    }

    setDevices(devices);
    setSelectedDevice(device);
    setShow(true);
  };

  const handleVideoClick = () => {
    if (videoRef.current) {
      readAndCacheVideoFrame(videoRef.current!).then((data) => {
        if (!data) return;
        setCurrentImage(data);
        setShow(false);
      });
    }
  };

  useEffect(() => {
    if (selectedDevice) {
      startVideo(selectedDevice.deviceId);
      localStorage.setItem(
        "selected-device",
        JSON.stringify({ deviceId: selectedDevice.deviceId })
      );
    }
  }, [selectedDevice]);

  return (
    <>
      {show && (
        <div className={styles.videooverlay}>
          <div className={styles.videoimagepicker}>
            <div className={styles.videobox}>
              <div className={styles.header}>
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
                {showCamera && (
                  <div className="button" onClick={() => handleVideoClick()}>
                    <HiOutlineVideoCamera size={24} className="buttonIcon" />
                  </div>
                )}
                <button className="button" onClick={() => setShow(false)}>
                  <GrClose size={24} className="buttonIcon" />
                </button>
              </div>
              <div className={styles.video}>
                <video
                  ref={videoRef}
                  autoPlay={true}
                  className={styles.videoelement}
                  title="Click to take a picture"
                  onClick={() => handleVideoClick()}
                ></video>
              </div>
            </div>
          </div>
        </div>
      )}
      <button
        title="Use Video Image"
        className={"button"}
        onClick={() => showVideo()}
      >
        <HiOutlineVideoCamera className={"buttonIcon"} />
      </button>
    </>
  );
};

export default VideoImagePicker;
