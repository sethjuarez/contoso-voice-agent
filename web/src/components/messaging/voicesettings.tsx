import { useLocalStorage } from "@/store/uselocalstorage";
import { useMediaDevices } from "@/store/usemediadevice";
import { GrPowerReset } from "react-icons/gr";
import styles from "./voicesettings.module.css";
import { defaultConfiguration, type VoiceConfiguration } from "@/store/voice";

const VoiceSettings = () => {
  const {
    storedValue: settings,
    setValue: setSettings,
    reset: resetSettings,
  } = useLocalStorage<VoiceConfiguration>(
    "voice-settings",
    defaultConfiguration
  );
  const { devices, error, isLoading } = useMediaDevices(true);

  return (
    <div className={styles.container}>
      <div className={styles.control}>
        <div className={styles.label}>Voice Input:</div>
        <select
          id="device"
          name="device"
          className={styles.mediaselect}
          value={settings.inputDeviceId}
          title="Select a device"
          onChange={(e) =>
            setSettings({ ...settings, inputDeviceId: e.target.value })
          }
        >
          {isLoading && <option>Loading...</option>}
          {error && <option>Error: {error}</option>}
          {devices
            .filter((device) => device.kind === "audioinput")
            .map((device) => {
              return (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label}
                </option>
              );
            })}
        </select>
      </div>

      <div className={styles.control}>
        <div className={styles.label}>
          Sensitivity Threshold (between 0 - 1):
        </div>
        <input
          id="threshold"
          name="threshold"
          type="number"
          title="Sensitivity Threshold"
          min={0}
          max={1}
          step={0.1}
          className={styles.textInput}
          value={settings.threshold}
          onChange={(e) =>
            setSettings({ ...settings, threshold: +e.target.value })
          }
        />
      </div>
      <div className={styles.control}>
        <div className={styles.label}>Silence Duration (in ms):</div>
        <input
          id="silence"
          name="chat"
          type="number"
          title="Silence Duration"
          min={0}
          max={3000}
          step={50}
          className={styles.textInput}
          value={settings.silence}
          onChange={(e) =>
            setSettings({ ...settings, silence: +e.target.value })
          }
        />
      </div>

      <div className={styles.control}>
        <div className={styles.label}>Prefix Padding (in ms):</div>
        <input
          id="prefix"
          name="chat"
          type="number"
          title="Prefix Padding"
          min={0}
          max={3000}
          step={50}
          className={styles.textInput}
          value={settings.prefix}
          onChange={(e) =>
            setSettings({ ...settings, prefix: +e.target.value })
          }
        />
      </div>
      <div className={styles.buttonContainer}>
        <button
          className={styles.resetButton}
          onClick={() => resetSettings()}
          title="Reset to default settings"
        >
          <GrPowerReset size={24} />
        </button>
      </div>
    </div>
  );
};

export default VoiceSettings;
