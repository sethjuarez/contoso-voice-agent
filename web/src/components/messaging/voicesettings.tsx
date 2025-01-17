import { useEffect, useState } from "react";
import VoiceInput from "./voiceinput";
import styles from "./voicesettings.module.css";
import { getSettings, Settings } from "@/socket/settings";
import { GrPowerReset } from "react-icons/gr";

const VoiceSettings = () => {
  const [settings, setSettings] = useState<Settings>({
    threshold: 0.8,
    silence: 500,
    prefix: 300,
  });

  useEffect(() => {
    const settings = getSettings();
    setSettings(settings);
  }, []);

  const saveSettings = (settings: Settings) => {
    setSettings(settings);
    localStorage.setItem("voice-settings", JSON.stringify(settings));
  };

  return (
    <div className={styles.container}>
      <div className={styles.control}>
        <div className={styles.label}>Voice Input:</div>
        <VoiceInput />
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
            saveSettings({ ...settings, threshold: +e.target.value })
          }
        />
      </div>
      <div>
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
            saveSettings({ ...settings, silence: +e.target.value })
          }
        />
      </div>

      <div>
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
            saveSettings({ ...settings, prefix: +e.target.value })
          }
        />
      </div>
      <div className={styles.buttonContainer}>
        <button
          className={styles.resetButton}
          onClick={() =>
            saveSettings({ threshold: 0.8, silence: 500, prefix: 300 })
          }
        >
          <GrPowerReset size={24} />
        </button>
      </div>
    </div>
  );
};

export default VoiceSettings;
